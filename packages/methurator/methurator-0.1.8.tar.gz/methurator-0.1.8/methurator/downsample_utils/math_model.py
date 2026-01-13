import warnings
import numpy as np
from scipy.optimize import curve_fit, OptimizeWarning

# ===============================================================
# Mathematical Model
# ===============================================================


def asymptotic_growth(x, beta0, beta1):
    """Asymptotic growth model using the arctangent function."""
    return beta0 * np.arctan(beta1 * x)


def derivative_asymptotic_growth(x, beta0, beta1):
    """Derivative of the asymptotic growth model."""
    return beta0 * beta1 / (1 + (beta1 * x) ** 2)


def find_asymptote(params):
    """Return the asymptote value (y-limit as x → ∞)."""
    beta0, _ = params
    return beta0 * np.pi / 2


def fit_saturation_model(x_data, y_data):
    """Fit the asymptotic growth model to observed data.

    Args:
        x_data: Array of x values (downsampling percentages)
        y_data: Array of y values (CpG counts)

    Returns:
        dict with keys:
            - fit_success: bool
            - params: tuple (beta0, beta1) or None if failed
            - asymptote: float or None if failed
            - fit_error: str or None if succeeded
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", OptimizeWarning)
            params, _ = curve_fit(asymptotic_growth, x_data, y_data, p0=[1, 1])
            asymptote = find_asymptote(params)
            return {
                "fit_success": True,
                "params": params,
                "asymptote": asymptote,
                "fit_error": None,
            }
    except (RuntimeError, OptimizeWarning) as e:
        return {
            "fit_success": False,
            "params": None,
            "asymptote": None,
            "fit_error": str(e),
        }
