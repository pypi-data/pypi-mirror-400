import numpy as np


def fill_nodata(
    arr: np.ndarray,
    nodata_value=None
) -> np.ndarray:
    """
    Replace nodata values with local mean.
    """
    data = arr.astype(float)

    if nodata_value is not None:
        data[data == nodata_value] = np.nan

    mask = np.isnan(data)
    if mask.any():
        mean_val = np.nanmean(data)
        data[mask] = mean_val

    return data


def normalize_minmax(arr: np.ndarray) -> np.ndarray:
    """
    Min–max normalization to [0, 1].
    """
    arr = arr.astype(float)
    min_val = np.nanmin(arr)
    max_val = np.nanmax(arr)

    if max_val - min_val < 1e-8:
        return np.zeros_like(arr)

    return (arr - min_val) / (max_val - min_val)


def prepare_dem(dem: np.ndarray) -> np.ndarray:
    """
    Full DEM preprocessing pipeline.
    """
    dem = fill_nodata(dem)
    dem = normalize_minmax(dem)
    return dem
