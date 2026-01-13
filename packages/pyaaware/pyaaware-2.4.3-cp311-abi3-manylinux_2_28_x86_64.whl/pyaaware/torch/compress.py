import torch

_POWER_COMPRESSION_FACTOR = 0.3


def _reconstruct_complex(magnitude: torch.Tensor, phase: torch.Tensor) -> torch.Tensor:
    """Reconstruct complex number from magnitude and phase.

    :param magnitude: Magnitude array
    :param phase: Phase array
    :return: Complex-valued array
    """
    real_part = magnitude * torch.cos(phase)
    imag_part = magnitude * torch.sin(phase)
    return real_part + 1j * imag_part


def power_compress(feature: torch.Tensor) -> torch.Tensor:
    """Compress a complex-valued feature.

    :param feature: A complex-valued array representing the feature.
    :return: A power-compressed complex-valued array.
    """
    magnitude = torch.abs(feature)
    phase = torch.angle(feature)
    compressed_magnitude = magnitude ** _POWER_COMPRESSION_FACTOR
    return _reconstruct_complex(compressed_magnitude, phase)


def power_uncompress(feature: torch.Tensor) -> torch.Tensor:
    """Uncompress a power-compressed complex-valued feature.

    :param feature: A complex-valued array representing the power-compressed feature.
    :return: A power-uncompressed complex-valued array.
    """
    magnitude = torch.abs(feature)
    phase = torch.angle(feature)
    uncompressed_magnitude = magnitude ** (1.0 / _POWER_COMPRESSION_FACTOR)
    return _reconstruct_complex(uncompressed_magnitude, phase)
