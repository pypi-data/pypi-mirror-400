"""
Read information from a [volume tracking matrix](https://flexela-docs.pages.dev/api/OutputFiles#volmetrackingmatrix)
(VTM) file
"""

from dataclasses import dataclass
import numpy as np

from scipy.sparse import csr_matrix


_TYPES = {
    "RC": np.uint32,
    "NNZ": np.uint32,
    "ROW_INDEX": np.uint32,
    "COLUMN_INDEX": np.uint32,
    "VALUES": np.double
}


@dataclass(frozen=True, eq=False)
class VTMData:
    """
    Raw data from a VTM file
    """
    _row_count: int
    _nnz: int
    _row_index: np.ndarray
    _column_index: np.ndarray
    _values: np.ndarray

    def to_csr(self, column_count: int) -> csr_matrix:
        """
        Convert into a SciPy
        [Compressed Sparse Row](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html)
        matrix

        :param column_count: number of columns in the matrix
        :type column_count: int
        """
        return csr_matrix(
            (self._values, self._column_index-1, np.concatenate(([0], self._row_index))),
            shape=(self._row_count, column_count)
        )


def read_vtm(path) -> VTMData:
    """
    Read the volume tracking matrix file

    :param path: filepath
    """
    with open(path, mode="rb") as f:
        # read the header
        row_count = np.fromfile(f, _TYPES["RC"], count=1).item()
        nnz = np.fromfile(f, _TYPES["NNZ"], count=1).item()

        # read the data
        row_index = np.fromfile(f, _TYPES["ROW_INDEX"], count=row_count)
        column_index = np.fromfile(f, _TYPES["COLUMN_INDEX"], count=nnz)
        values = np.fromfile(f, _TYPES["VALUES"], count=nnz)

    # verify the file by checking that ROW_INDEX(end)==NNZ
    if row_index[-1] != nnz:
        raise RuntimeError(f"ROW_INDEX and NNZ do not match in {path}")

    return VTMData(row_count, nnz, row_index, column_index, values)
