import pytest
import numpy as np
import sys
import os

# Ensure we can import numpy_frame from src
# Append 'src' to sys.path so 'import numpy_frame' works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from numpy_frame import NumpyFrame

@pytest.fixture
def sample_data():
    data = np.arange(12).reshape(4, 3)
    cols = ["a", "b", "c"]
    return data, cols

def test_init(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    assert nf.columns == cols
    np.testing.assert_array_equal(nf.data, data)

def test_init_mismatch():
    data = np.zeros((4, 3))
    cols = ["a", "b"] # Only 2 names, but 3 columns
    with pytest.raises(ValueError, match="Shape mismatch"):
        NumpyFrame(data, cols)

def test_getitem_single_column(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    # "a" is column 0 -> [0, 3, 6, 9]
    col_a = nf["a"]
    expected = np.array([0, 3, 6, 9])
    np.testing.assert_array_equal(col_a, expected)

def test_getitem_multiple_columns(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    # ["a", "c"] -> columns 0 and 2
    subset = nf[["a", "c"]]
    assert isinstance(subset, NumpyFrame)
    assert subset.columns == ["a", "c"]
    
    expected_data = data[:, [0, 2]]
    np.testing.assert_array_equal(subset.data, expected_data)

def test_getitem_slice(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    # Slice rows 0:2
    subset = nf[0:2]
    assert isinstance(subset, NumpyFrame)
    assert subset.columns == cols
    
    expected_data = data[0:2, :]
    np.testing.assert_array_equal(subset.data, expected_data)

def test_getitem_single_row_int(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    # Row 1 -> [3, 4, 5]
    row = nf[1]
    # Should be a numpy array, not a frame (based on current implementation)
    assert isinstance(row, np.ndarray)
    np.testing.assert_array_equal(row, data[1])

def test_getitem_invalid_column(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    with pytest.raises(KeyError, match="Column 'z' not found"):
        _ = nf["z"]

def test_repr(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    r = repr(nf)
    assert "NumpyFrame(columns=['a', 'b', 'c'])" in r
    
    # Normalize whitespace to avoid issues with numpy's formatting (e.g. extra spaces)
    r_normalized = "".join(r.split())
    data_normalized = "".join(str(data).split())
    assert data_normalized in r_normalized

def test_getitem_tuple_rows_and_cols(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    # slice rows 0:2, cols ["a", "c"]
    subset = nf[0:2, ["a", "c"]]
    assert isinstance(subset, NumpyFrame)
    assert subset.columns == ["a", "c"]
    
    expected_data = data[0:2, [0, 2]]
    np.testing.assert_array_equal(subset.data, expected_data)

def test_getitem_tuple_rows_and_single_col(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    # slice rows 0:2, col "b" -> returns 1D array
    # because selecting single col returns array, slicing that array returns array
    col_b_slice = nf[0:2, "b"]
    assert isinstance(col_b_slice, np.ndarray)
    
    expected_data = data[0:2, 1]
    np.testing.assert_array_equal(col_b_slice, expected_data)

def test_getitem_list_rows_and_cols(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    # Rows [0, 2], Cols ["a", "c"]
    subset = nf[[0, 2], ["a", "c"]]
    assert isinstance(subset, NumpyFrame)
    assert subset.columns == ["a", "c"]
    
    # Expected: data at (0,0), (0,2), (2,0), (2,2)
    # Using np.ix_ to construct expected
    expected_data = data[np.ix_([0, 2], [0, 2])]
    np.testing.assert_array_equal(subset.data, expected_data)

def test_getitem_list_rows_and_single_col(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    # Rows [1, 3], Col "b"
    subset = nf[[1, 3], "b"]
    assert isinstance(subset, np.ndarray)
    
    expected_data = data[[1, 3], 1]
    np.testing.assert_array_equal(subset, expected_data)

def test_groupby_sum():
    # Data:
    # 0: [1, 2, 3]
    # 1: [1, 10, 20]
    # 2: [2, 5, 5]
    # 3: [2, 1, 1]
    
    data = np.array([
        [1, 2, 3],
        [1, 10, 20],
        [2, 5, 5],
        [2, 1, 1]
    ])
    cols = ["g", "a", "b"]
    nf = NumpyFrame(data, cols)
    
    gb = nf.groupby("g")
    
    # Expected sum by g:
    # g=1: a=2+10=12, b=3+20=23
    # g=2: a=5+1=6, b=5+1=6
    # Res: [[1, 12, 23], [2, 6, 6]]
    
    res = gb.sum()
    assert isinstance(res, NumpyFrame)
    assert res.columns == ["g", "a", "b"] # default order group first
    
    expected = np.array([
        [1, 12, 23],
        [2, 6, 6]
    ])
    np.testing.assert_array_equal(res.data, expected)

def test_groupby_mean():
    data = np.array([
        [1, 2.0],
        [1, 4.0],
        [3, 9.0]
    ])
    # Note: Using float data if testing mean usually better, but numpy handles it. 
    # Our init doesn't enforce dtype, so it's whatever numpy array is.
    
    cols = ["g", "val"]
    nf = NumpyFrame(data, cols)
    res = nf.groupby("g").mean()
    
    # g=1: mean(2, 4) = 3
    # g=3: mean(9) = 9
    
    expected = np.array([
        [1., 3.],
        [3., 9.]
    ])
    np.testing.assert_array_equal(res.data, expected)

def test_array_protocol(sample_data):
    data, cols = sample_data
    nf = NumpyFrame(data, cols)
    
    # Test np.array(nf)
    arr = np.array(nf)
    
    # Needs to be equal to underlying data
    np.testing.assert_array_equal(arr, data)
    
    # Test explicit type conversion
    arr_float = np.array(nf, dtype=float)
    assert arr_float.dtype == float

