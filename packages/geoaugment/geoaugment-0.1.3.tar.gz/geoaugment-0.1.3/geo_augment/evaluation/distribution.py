import numpy as np


def summarize_distribution(arr: np.ndarray) -> dict:
    """
    Compute basic distribution statistics for a flood-risk surface.
    """
    return {
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "p5": float(np.percentile(arr, 5)),
        "p50": float(np.percentile(arr, 50)),
        "p95": float(np.percentile(arr, 95)),
    }


def compare_distributions(reference: np.ndarray, synthetic: np.ndarray) -> dict:
    """
    Compare reference and synthetic flood-risk distributions.
    """
    return {
        "reference": summarize_distribution(reference),
        "synthetic": summarize_distribution(synthetic),
        "mean_shift": float(np.mean(synthetic) - np.mean(reference)),
        "std_ratio": float(np.std(synthetic) / (np.std(reference) + 1e-8)),
    }
