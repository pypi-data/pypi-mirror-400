# NumpyFrame

A lightweight wrapper around numpy arrays that provides DataFrame-like functionality with minimal dependencies.

## Features
- **Column Selection**: Access columns by name (O(1) lookup).
- **Indexing & Slicing**: 
  - `nf["col"]` -> 1D array
  - `nf[["col1", "col2"]]` -> Sub-frame
  - `nf[0:5]` -> Row slice
  - `nf[[0, 2], ["a", "b"]]` -> Advanced rectangular indexing (Train/Test split friendly!)
- **GroupBy**: Split-Apply-Combine with `.groupby("col").mean()` or `.sum()`.
- **Fast**: Built purely on top of numpy.

## Installation

```bash
pip install numpy_frame
```

## Usage

```python
import numpy as np
from numpy_frame import NumpyFrame

# Create data
data = np.arange(12).reshape(4, 3)
cols = ["a", "b", "c"]
nf = NumpyFrame(data, cols)

# 1. Column Access
print(nf["a"])

# 2. Slicing
subset = nf[:2, ["a", "c"]] 

# 3. Advanced Indexing (e.g. random rows)
random_rows = [0, 3]
train_set = nf[random_rows, ["a", "b"]]

# 4. GroupBy
# Suppose column 'a' has groups
nf_grouped = nf.groupby("a").sum()
print(nf_grouped)
```

## License
MIT