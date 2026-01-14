import numpy as np
from scipy.ndimage import gaussian_filter


# --------------------------------------------------
# 1. Distribution checks
# --------------------------------------------------

def distribution_summary(
    field: np.ndarray,
    name: str | None = None,
) -> dict:
    """
    Summarize statistical properties of a continuous flood risk surface.

    Parameters
    ----------
    field : np.ndarray
        Flood risk values in [0, 1]
    name : optional str
        Label for logging or reporting

    Returns
    -------
    dict
        Mean, std, min, max, percentiles
    """

    if field.ndim != 2:
        raise ValueError("Flood risk field must be 2D")

    summary = {
        "mean": float(np.mean(field)),
        "std": float(np.std(field)),
        "min": float(np.min(field)),
        "max": float(np.max(field)),
        "p10": float(np.percentile(field, 10)),
        "p50": float(np.percentile(field, 50)),
        "p90": float(np.percentile(field, 90)),
    }

    if name:
        summary["name"] = name # type: ignore

    return summary


# --------------------------------------------------
# 2. Spatial coherence checks
# --------------------------------------------------

def spatial_correlation(
    field: np.ndarray,
    sigma: float = 5.0,
) -> float:
    """
    Measure spatial smoothness via correlation with a smoothed version.

    High correlation => spatially coherent risk patterns.

    Parameters
    ----------
    field : np.ndarray
        Flood risk surface
    sigma : float
        Gaussian smoothing strength

    Returns
    -------
    float
        Pearson correlation coefficient
    """

    if field.ndim != 2:
        raise ValueError("Flood risk field must be 2D")

    smoothed = gaussian_filter(field, sigma=sigma)

    f = field.flatten()
    s = smoothed.flatten()

    if np.std(f) == 0 or np.std(s) == 0:
        return 0.0

    corr = np.corrcoef(f, s)[0, 1]
    return float(corr)


# --------------------------------------------------
# 3. Flooded area ratios
# --------------------------------------------------

def flooded_area_ratio(
    field: np.ndarray,
    threshold: float = 0.7,
) -> float:
    """
    Compute fraction of area exceeding a flood-risk threshold.

    This answers:
    'How much of the map is considered high-risk?'

    Parameters
    ----------
    field : np.ndarray
        Continuous flood risk surface
    threshold : float
        Risk cutoff in [0, 1]

    Returns
    -------
    float
        Area ratio (0–1)
    """

    if not (0.0 < threshold < 1.0):
        raise ValueError("Threshold must be in (0, 1)")

    flooded = field >= threshold
    return float(np.mean(flooded))
