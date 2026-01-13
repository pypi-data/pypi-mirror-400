import pytest
import numpy as np

import ela_reader.formats.vtm_reader as vtm_reader

TEST_VTM_PATH = "tests/resources/vtm.bin"
TEST_VTM_SOLUTION = [
    [10, 20,  0,  0,  0,  0],
    [0, 30,  0, 40,  0,  0],
    [0,  0, 50, 60, 70,  0],
    [0,  0,  0,  0,  0, 80]
]


@pytest.fixture
def test_vtm_data():
    return vtm_reader.VTMData(
        _row_count=4,
        _nnz=8,
        _row_index=np.array([2, 4, 7, 8], dtype=vtm_reader._TYPES["ROW_INDEX"]),
        _column_index=np.array([1, 2, 2, 4, 3, 4, 5, 6], dtype=vtm_reader._TYPES["COLUMN_INDEX"]),
        _values=np.array([10, 20, 30, 40, 50, 60, 70, 80], dtype=vtm_reader._TYPES["VALUES"])
    )


def test_vtm_reader(test_vtm_data):
    """Test reading the file"""
    vtm_data = vtm_reader.read_vtm(TEST_VTM_PATH)

    assert vtm_data._row_count == test_vtm_data._row_count
    assert vtm_data._nnz == test_vtm_data._nnz
    assert np.array_equal(vtm_data._row_index, test_vtm_data._row_index)
    assert np.array_equal(vtm_data._column_index, test_vtm_data._column_index)
    assert np.array_equal(vtm_data._values, test_vtm_data._values)


def test_to_cst(test_vtm_data):
    """Test conversion to CSR"""
    Q = test_vtm_data.to_csr(column_count=6).toarray()
    assert np.array_equal(Q, TEST_VTM_SOLUTION)
