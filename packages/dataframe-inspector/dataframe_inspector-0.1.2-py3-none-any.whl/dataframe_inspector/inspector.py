"""
Core inspector functionality for exploring nested structures in DataFrame columns.
"""

from typing import Any, Set
import pandas as pd


class Inspector:
    """
    Inspector for understanding nested dict/list structures in pandas DataFrame columns.

    Example:
        import pandas as pd
        from dataframe_inspector import Inspector

        df = pd.DataFrame({
            'data': [
                {'user': {'name': 'Alice', 'id': 1}},
                {'user': {'name': 'Bob', 'id': 2}}
            ]
        })
        inspector = Inspector(df) # See what's in the DataFrame
        inspector.overview() # Deep dive
        inspector.inspect_column('data')
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize inspector with a DataFrame.

        Args:
            df: pandas DataFrame to inspect
        """
        self.df = df

    def overview(self) -> None:
        """
        Quick overview of the entire DataFrame.

        Shows:
        - Basic dimensions (rows, columns)
        - Nested columns (candidates for inspect_column)
        - Simple columns with basic stats
        - Missing data summary

        This is the recommended first step when exploring a new DataFrame.
        Use inspect_column() for detailed inspection of specific nested columns.

        Example:
            inspector = Inspector(df)
            inspector.overview()  # See what's in the DataFrame
            inspector.inspect_column('nested_col')  # Deep dive
        """
        print(f"\n{'='*80}")
        print("DATAFRAME OVERVIEW")
        print(f"{'='*80}")

        # Basic info
        print("\n📊 Dimensions:")
        print(f"  Rows: {len(self.df):,}")
        print(f"  Columns: {len(self.df.columns)}")

        # Identify nested vs simple columns
        nested_cols = []
        simple_cols = []

        for col in self.df.columns:
            if self.df[col].dtype == "object":
                # Check first three non-null value to detect dict/list
                sample = self.df[col].dropna().head(3)
                is_nested = False
                for val in sample:
                    if isinstance(val, (dict, list)):
                        is_nested = True
                        break

                if is_nested:
                    nested_cols.append(col)
                else:
                    simple_cols.append(col)
            else:
                simple_cols.append(col)

        # Show nested columns (the main use case)
        if nested_cols:
            print(f"\n🔍 Nested Columns ({len(nested_cols)}):")
            print("  Use inspect_column() to explore these:")
            for col in nested_cols:
                null_pct = (self.df[col].isna().sum() / len(self.df)) * 100
                print(f"  - {col} ({null_pct:.1f}% null)")

        # Show simple columns summary
        if simple_cols:
            print(f"\n📝 Simple Columns ({len(simple_cols)}):")
            for col in simple_cols[:10]:
                dtype = self.df[col].dtype
                null_pct = (self.df[col].isna().sum() / len(self.df)) * 100
                unique = self.df[col].nunique()
                print(f"  - {col} ({dtype}, {unique} unique, {null_pct:.1f}% null)")
            if len(simple_cols) > 10:
                print(f"  ... and {len(simple_cols) - 10} more")

        print(f"\n{'='*80}\n")

    def inspect_column(
        self, column: str, sample_size: int = 3, max_depth: int = 3
    ) -> None:
        """
        Deep inspection of nested JSON/dict columns.

        Args:
            column: Column name to inspect
            sample_size: Number of samples to show (default: 3)
            max_depth: Maximum depth to traverse in nested structure (default: 3)

        Example:
            inspector.inspect_column('response', sample_size=5, max_depth=4)
        """
        if column not in self.df.columns:
            print(f"❌ Column '{column}' not found in DataFrame")
            return

        print(f"\n{'='*60}")
        print(f"Nested Column: '{column}'")
        print(f"{'='*60}")

        # Find all keys in nested structures
        all_keys = self._find_nested_keys(column, max_depth=max_depth)

        print(f"\nNested structure keys found (depth ≤ {max_depth}):")
        for key_path in sorted(all_keys):
            print(f"  - {key_path}")

        print(f"\nSample values (first {sample_size}):")
        for idx, val in self.df[column].head(sample_size).items():
            print(f"\n[Row {idx}]:")
            self._print_structure(val, indent=2)

        print(f"{'='*60}\n")

    def _find_nested_keys(
        self, column: str, max_depth: int, sample_size: int = 3
    ) -> Set[str]:
        """Find all keys in nested dict/list structures."""
        all_keys = set()

        # Sample to avoid processing too many rows for large DataFrames
        sample_data = self.df[column].dropna().head(sample_size)

        for val in sample_data:
            keys = self._extract_keys_recursive(
                val, prefix="", max_depth=max_depth, current_depth=0
            )
            all_keys.update(keys)

        return all_keys

    def _extract_keys_recursive(
        self, obj: Any, prefix: str, max_depth: int, current_depth: int
    ) -> Set[str]:
        """Recursively extract keys from nested structure."""
        if current_depth >= max_depth:
            return set()

        keys = set()

        if isinstance(obj, dict):
            for key, value in obj.items():
                key_path = f"{prefix}.{key}" if prefix else key
                keys.add(key_path)
                keys.update(
                    self._extract_keys_recursive(
                        value, key_path, max_depth, current_depth + 1
                    )
                )
        elif isinstance(obj, list) and obj:
            # Check first item in list
            keys.add(f"{prefix}[0]" if prefix else "[0]")
            keys.update(
                self._extract_keys_recursive(
                    obj[0],
                    f"{prefix}[0]" if prefix else "[0]",
                    max_depth,
                    current_depth + 1,
                )
            )

        return keys

    def _print_structure(self, obj: Any, indent: int = 0, max_items: int = 10) -> None:
        """Pretty print nested structure with indentation."""
        indent_str = "  " * indent

        if isinstance(obj, dict):
            items = list(obj.items())[:max_items]
            for key, value in items:
                if isinstance(value, (dict, list)):
                    print(f"{indent_str}{key}:")
                    self._print_structure(value, indent + 1, max_items)
                else:
                    val_str = str(value)
                    if len(val_str) > 100:
                        val_str = val_str[:100] + "..."
                    print(f"{indent_str}{key}: {val_str}")

            if len(obj) > max_items:
                print(f"{indent_str}... ({len(obj) - max_items} more items)")

        elif isinstance(obj, list):
            items = obj[:max_items]
            for i, item in enumerate(items):
                if isinstance(item, (dict, list)):
                    print(f"{indent_str}[{i}]:")
                    self._print_structure(item, indent + 1, max_items)
                else:
                    val_str = str(item)
                    if len(val_str) > 100:
                        val_str = val_str[:100] + "..."
                    print(f"{indent_str}[{i}]: {val_str}")

            if len(obj) > max_items:
                print(f"{indent_str}... ({len(obj) - max_items} more items)")

        else:
            val_str = str(obj)
            if len(val_str) > 200:
                val_str = val_str[:200] + "..."
            print(f"{indent_str}{val_str}")
