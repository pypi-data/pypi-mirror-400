import numpy as np
from scipy.interpolate import interp1d

_lookuptable = np.linspace(0, np.pi + 1e-9, 10001)
_sinc_values = np.sinc(_lookuptable / np.pi)

_interpolator = interp1d(
    x=_sinc_values,
    y=_lookuptable,
    kind='linear',
    bounds_error=False,
    fill_value=(0, np.pi)
)


def inv_sinc(x):
    """Inverse Sinc function.

    Args:
        x (float or np.ndarray): Normalized Amplitude (0.0 ~ 1.0)

    Returns:
        float or np.ndarray: Phase value (0.0 ~ -pi)
    """
    return _interpolator(x)


_lookuptable_minus = np.linspace(-np.pi, 0, 10001)
_sinc_values_minus = np.sinc(_lookuptable_minus / np.pi)

_interpolator_minus = interp1d(
    x=_sinc_values_minus,
    y=_lookuptable_minus,
    kind='linear',
    bounds_error=False,
    fill_value=(-np.pi, 0)
)


def inv_sinc_minus(x):
    """Inverse Sinc function in minus domain.

    Args:
        x (float or np.ndarray): Normalized Amplitude (0.0 ~ 1.0)

    Returns:
        float or np.ndarray: Phase value (-pi ~ 0.0)
    """
    return _interpolator_minus(x)
