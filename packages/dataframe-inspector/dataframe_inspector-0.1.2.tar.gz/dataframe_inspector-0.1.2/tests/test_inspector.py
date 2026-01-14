"""
Tests for dataframe-inspector.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataframe_inspector import Inspector


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Create a sample DataFrame with nested data."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "nested": [
                {
                    "user": {"name": "Alice", "id": 100},
                    "metadata": {"created": "2024-01-01"},
                },
                {
                    "user": {"name": "Bob", "id": 200},
                    "metadata": {"created": "2024-01-02"},
                },
                {
                    "user": {"name": "Charlie", "id": 300},
                    "metadata": {"created": "2024-01-03"},
                },
            ],
        }
    )


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """Create an empty DataFrame."""
    return pd.DataFrame()


@pytest.fixture
def simple_df() -> pd.DataFrame:
    """Create a DataFrame with only simple columns."""
    return pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})


# pylint: disable=redefined-outer-name
class TestInspector:
    """Test Inspector functionality."""

    def test_initialization(self, sample_df: pd.DataFrame) -> None:
        """Test inspector initialization."""
        inspector = Inspector(sample_df)
        assert inspector.df is not None
        assert len(inspector.df) == 3

    def test_overview_with_nested_columns(
        self, sample_df: pd.DataFrame, capsys
    ) -> None:
        """Test overview with nested columns."""
        inspector = Inspector(sample_df)
        inspector.overview()

        captured = capsys.readouterr()
        assert "DATAFRAME OVERVIEW" in captured.out
        assert "Rows: 3" in captured.out
        assert "Columns: 3" in captured.out
        assert "Nested Columns" in captured.out
        assert "nested" in captured.out

    def test_overview_simple_dataframe(self, simple_df: pd.DataFrame, capsys) -> None:
        """Test overview with only simple columns."""
        inspector = Inspector(simple_df)
        inspector.overview()

        captured = capsys.readouterr()
        assert "DATAFRAME OVERVIEW" in captured.out
        assert "Simple Columns" in captured.out
        assert "Nested Columns" not in captured.out

    def test_overview_empty_dataframe(self, empty_df: pd.DataFrame, capsys) -> None:
        """Test overview with empty DataFrame."""
        inspector = Inspector(empty_df)
        inspector.overview()

        captured = capsys.readouterr()
        assert "DATAFRAME OVERVIEW" in captured.out
        assert "Rows: 0" in captured.out
        assert "Columns: 0" in captured.out

    def test_inspect_column(self, sample_df: pd.DataFrame, capsys) -> None:
        """Test inspect_column functionality."""
        inspector = Inspector(sample_df)
        inspector.inspect_column("nested", sample_size=2, max_depth=3)

        captured = capsys.readouterr()
        assert "Nested Column: 'nested'" in captured.out
        assert "user" in captured.out
        assert "user.name" in captured.out
        assert "metadata" in captured.out

    def test_inspect_column_missing(self, sample_df: pd.DataFrame, capsys) -> None:
        """Test inspect_column with missing column."""
        inspector = Inspector(sample_df)
        inspector.inspect_column("nonexistent")

        captured = capsys.readouterr()
        assert "not found" in captured.out
