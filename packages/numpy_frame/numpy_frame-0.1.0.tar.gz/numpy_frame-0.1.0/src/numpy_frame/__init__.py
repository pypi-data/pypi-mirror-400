from typing import List, Union, Dict, Any, Tuple
import numpy as np


class NumpyFrame:
    """A lightweight wrapper around numpy arrays for DataFrame-like functionality.

    This class provides efficient column mapping, slicing, and groupby capabilities,
    built strictly on top of numpy ndarrays.

    Attributes:
        data (np.ndarray): The underlying 2D numpy array containing the data.
        columns (List[str]): The list of column names.
    """

    def __init__(self, data: np.ndarray, columns: List[str]):
        """Initialize a NumpyFrame.

        Args:
            data (np.ndarray): A 2D numpy array (shape: rows x cols).
            columns (List[str]): List of column names corresponding to the second dimension of data.

        Raises:
            ValueError: If the number of columns in data does not match the number of column names.
        """
        if data.shape[1] != len(columns):
            raise ValueError(
                f"Shape mismatch: data has {data.shape[1]} columns, but {len(columns)} column names provided."
            )

        self.data = data
        self.columns = columns
        self._col_map: Dict[str, int] = {name: i for i, name in enumerate(columns)}

    def __getitem__(
        self, key: Union[str, List[str], slice, int, tuple]
    ) -> Union[np.ndarray, "NumpyFrame"]:
        """Retrieve data using column names, slices, or advanced indexing.

        Supported Access Patterns:
        1. Single column: `nf['col']` -> np.ndarray (1D)
        2. Multiple columns: `nf[['col1', 'col2']]` -> NumpyFrame
        3. Row slicing: `nf[0:5]` -> NumpyFrame
        4. Tuple indexing: `nf[rows, cols]` (e.g., `nf[:2, ['a', 'b']]`) -> NumpyFrame or np.ndarray
        5. Advanced row indexing: `nf[[0, 2], ['a', 'c']]` -> NumpyFrame

        Args:
            key: The selection key (string, list of strings, slice, int, tuple).

        Returns:
            Union[np.ndarray, NumpyFrame]: The selected subset of data.

        Raises:
            KeyError: If a requested column name is not found.
        """
        # 1. Handle Tuple (Rows, Cols)
        if isinstance(key, tuple):
            row_key, col_key = key

            # Resolve column key to indices
            if isinstance(col_key, str):
                col_indices = self._col_map[col_key]
                return self.data[row_key, col_indices]

            elif isinstance(col_key, list):
                col_indices = [self._col_map[k] for k in col_key]
                new_cols = col_key

                # Check for advanced indexing on rows (list or array of ints)
                if isinstance(row_key, (list, np.ndarray)):
                    # Rectangular selection using np.ix_
                    new_data = self.data[np.ix_(row_key, col_indices)]
                else:
                    # Standard slice index
                    new_data = self.data[row_key, col_indices]

                return NumpyFrame(new_data, new_cols)

            else:
                # Fallback to standard numpy behavior (e.g., if columns key is slicing/array)
                return self.data[key]

        # 2. Select by single column name -> return 1D array
        if isinstance(key, str):
            if key not in self._col_map:
                raise KeyError(f"Column '{key}' not found.")
            return self.data[:, self._col_map[key]]

        # 3. Select by list of column names -> return new NumpyFrame
        if isinstance(key, list):
            indices = [self._col_map[k] for k in key]
            return NumpyFrame(self.data[:, indices], key)

        # 4. Standard slicing (row slicing) -> return new NumpyFrame
        if isinstance(key, (slice, int, np.integer)):
            newdata = self.data[key]
            if isinstance(key, (int, np.integer)):
                return newdata
            return NumpyFrame(newdata, self.columns)

        return self.data[key]

    def __repr__(self) -> str:
        return f"NumpyFrame(columns={self.columns})\n{self.data}"
        
    def __array__(self, dtype=None, copy=None) -> np.ndarray:
        """Support for the numpy array protocol.
        
        Allows NumpyFrame to be passed to functions expecting an array (e.g. np.array(nf)).
        """
        # Handle logic for copy/dtype
        if dtype is None:
            res = self.data
        else:
            res = self.data.astype(dtype, copy=False)
            
        if copy is True:
            return res.copy()
        if copy is False:
            return res
        # Default behavior (copy=None): usually numpy prefers copy if not explicitly False? 
        # Actually standard behavior for __array__ usually implies returning array.
        # If we return self.data (reference), modifications affect original.
        # But for O(1) performance claims, we should avoid copy unless requested.
        return res

    def groupby(self, by: str) -> "NumpyFrameGroupBy":
        """Group the frame by values in a specific column.

        Args:
            by (str): The column name to group by.

        Returns:
            NumpyFrameGroupBy: A groupby object ready for aggregation.

        Raises:
            KeyError: If the column is not found.
        """
        if by not in self._col_map:
            raise KeyError(f"Column '{by}' not found")
        index = self._col_map[by]
        return NumpyFrameGroupBy(self, index, by)


class NumpyFrameGroupBy:
    """Helper class to handle groupby split-apply-combine operations.

    Identifies unique groups in the target column and maps them to row indices.
    """

    def __init__(self, frame: NumpyFrame, group_col_index: int, group_col_name: str):
        """Initialize the GroupBy object.

        Args:
            frame (NumpyFrame): The parent frame.
            group_col_index (int): Index of the grouping column.
            group_col_name (str): Name of the grouping column.
        """
        self.frame = frame
        self.group_col_index = group_col_index
        self.group_col_name = group_col_name

        col_data = self.frame.data[:, group_col_index]
        self.unique_groups = np.unique(col_data)

        self.groups = {}
        for val in self.unique_groups:
            # Note: This is O(G * N). For numeric types, argsort is better, but this is generic.
            self.groups[val] = np.where(col_data == val)[0]

    def __iter__(self):
        """Iterate over the groups, yielding (group_value, sub_frame)."""
        for group_val in self.unique_groups:
            indices = self.groups[group_val]
            subframe = self.frame[indices, self.frame.columns]
            yield group_val, subframe

    def _aggregate(self, func_name: str) -> NumpyFrame:
        """Internal helper to apply aggregation functions like 'mean' or 'sum'.

        Args:
            func_name (str): The name of the aggregation function.

        Returns:
            NumpyFrame: A new frame with the grouped results.
        """
        agg_data = []
        # Result columns: Grouping column + other columns
        res_cols = [self.group_col_name] + [
            c for c in self.frame.columns if c != self.group_col_name
        ]

        for group_val in self.unique_groups:
            indices = self.groups[group_val]
            group_rows = self.frame.data[indices]

            row_res = [group_val]

            for col_name in self.frame.columns:
                if col_name == self.group_col_name:
                    continue

                col_idx = self.frame._col_map[col_name]
                col_values = group_rows[:, col_idx]

                if func_name == "mean":
                    val = np.mean(col_values)
                elif func_name == "sum":
                    val = np.sum(col_values)
                else:
                    raise ValueError(f"Unknown aggregation: {func_name}")

                row_res.append(val)

            agg_data.append(row_res)

        return NumpyFrame(np.array(agg_data), res_cols)

    def mean(self) -> NumpyFrame:
        """Compute the mean of each group."""
        return self._aggregate("mean")

    def sum(self) -> NumpyFrame:
        """Compute the sum of each group."""
        return self._aggregate("sum")


if __name__ == "__main__":
    data = np.array([[1, 10, 100], [1, 20, 200], [2, 30, 300], [2, 40, 400]])
    cols = ["group", "val1", "val2"]
    nf = NumpyFrame(data, cols)

    # testing groupby sum
    agg_sum = nf.groupby("group").sum()
    print("Sum aggregation:\n", agg_sum.data)

    # testing groupby mean
    agg_mean = nf.groupby("group").mean()
    print("\nMean aggregation:\n", agg_mean.data)

    