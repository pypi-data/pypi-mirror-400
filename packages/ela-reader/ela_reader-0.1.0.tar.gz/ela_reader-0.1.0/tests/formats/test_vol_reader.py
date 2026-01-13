import pytest
import numpy as np

import ela_reader.formats.vol_reader as vol_reader

TEST_VOL_PATH = "tests/resources/vol.bin"
TEST_VOL_SOLUTION = [0.7, 10.0, 0.0, 0.0, 0.25]


@pytest.fixture
def test_vol_data():
    return vol_reader.VolData(
        _row_count=vol_reader._TYPES["RC"](len(TEST_VOL_SOLUTION)),
        _values=np.array(TEST_VOL_SOLUTION, dtype=vol_reader._TYPES["VALUES"])
    )


def test_vol_reader(test_vol_data):
    """Test reading the file"""
    vol_data = vol_reader.read_vol(TEST_VOL_PATH)

    assert vol_data._row_count == test_vol_data._row_count
    assert np.array_equal(vol_data._values, test_vol_data._values)


def test_to_numpy(test_vol_data):
    """Test conversion to ndarray"""
    v = test_vol_data.to_numpy()
    assert np.allclose(v, TEST_VOL_SOLUTION)
