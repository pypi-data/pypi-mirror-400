"""
Read information from a [time log](https://flexela-docs.pages.dev/api/OutputFiles#timelogbin)
"""

import numpy as np

_TYPES = {
    "Index": np.uint32,
    "RC": np.uint32,
    "Time": np.double
}

LOG_DTYPE = np.dtype([
    ("index", _TYPES["Index"]),
    ("row_count", _TYPES["RC"]),
    ("time", _TYPES["Time"])
])


def read_timelog(path) -> np.ndarray:
    """
    Read the timelog file

    :param path: filepath
    """
    with open(path, mode="rb") as f:
        return np.fromfile(f, dtype=LOG_DTYPE, count=-1)
