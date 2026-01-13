"""
Read information from a [volume vector](https://flexela-docs.pages.dev/api/OutputFiles#volumevector) file
"""

from dataclasses import dataclass
import numpy as np

_TYPES = {
    "RC": np.uint32,
    "VALUES": np.double
}


@dataclass(frozen=True)
class VolData:
    """
    Raw data from a volume vector file
    """
    _row_count: int
    _values: np.ndarray

    def to_numpy(self) -> np.ndarray:
        """
        Convert into a NumPy [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html)
        """
        return self._values


def read_vol(path) -> VolData:
    """
    Read the volume vector file

    :param path: filepath
    """
    with open(path, mode="rb") as f:
        # read the header
        row_count = np.fromfile(f, _TYPES["RC"], count=1).item()

        # read the data
        values = np.fromfile(f, _TYPES["VALUES"], count=row_count)

    return VolData(row_count, values)
