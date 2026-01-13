from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class FileParser:
    """Abstract base class for file parsers.

    Provides methods for checking file extensions and existence.
    """

    def check_extension(self, path: Path, extension: str) -> None:
        """Check if the file has the expected extension."""
        if isinstance(path, str):
            path = Path(path)

        if not path.suffix == extension:
            raise ValueError(f"Invalid file type: {path.suffix}. Expected {extension}.")

    def check_existence(self, path: Path) -> None:
        """Check if the file exists and is a file."""
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}.")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}.")

    def check_file(self, path: Path, extension: str) -> None:
        """Check if the file exists and has the expected extension."""
        if isinstance(path, str):
            path = Path(path)

        self.check_existence(path)
        self.check_extension(path, extension)

    def check_empty(self, df: pd.DataFrame) -> None:
        """Check if the DataFrame is empty."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame.")

        if df.empty:
            raise ValueError("No data found in the file.")

    def normalize_column_names(self, df: pd.DataFrame) -> None:
        # Remove empty columns
        df.drop(columns=[col for col in df.columns if col == ""], inplace=True)

        # Remove rows where all values are equal to the column names. Because sometimes header will be duplicated in the data.
        indexes = df[df.eq(df.columns).all(axis=1)].index
        df.drop(indexes, inplace=True)

        # Normalize column names: strip whitespace, convert to lowercase, and replace spaces with underscores
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
