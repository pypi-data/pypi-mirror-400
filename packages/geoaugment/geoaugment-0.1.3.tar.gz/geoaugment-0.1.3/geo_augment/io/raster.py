import rasterio
import numpy as np
from rasterio.windows import Window


class RasterLoader:
    """
    Safe raster reader for single-band geospatial rasters (e.g. DEM).
    """

    def __init__(self, path: str):
        self.path = path

    def read(self, masked: bool = True) -> np.ndarray:
        """
        Read full raster into memory.
        """
        with rasterio.open(self.path) as src:
            data = src.read(1, masked=masked)
        return data

    def metadata(self) -> dict:
        """
        Return raster metadata.
        """
        with rasterio.open(self.path) as src:
            return src.meta.copy()

    def read_window(
        self,
        row: int,
        col: int,
        size: int,
        masked: bool = True
    ) -> np.ndarray:
        """
        Read a square window from raster.
        """
        with rasterio.open(self.path) as src:
            window = Window(col, row, size, size)
            return src.read(1, window=window, masked=masked)
