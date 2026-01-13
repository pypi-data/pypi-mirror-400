from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from ..parser import FileParser

# Normalization factor to convert raw ADC counts to units of g.
SENS_NORMALIZATION_FACTOR = -4 / 512

# Numpy dtype for the binary structure:
# - timestamp: 6 bytes (48-bit int)
# - x, y, z: 2 bytes each, Big-Endian signed int16 (>i2)
DTYPE = np.dtype([("timestamp", "6uint8"), ("x", ">i2"), ("y", ">i2"), ("z", ">i2")])


@dataclass
class Sens(FileParser):
    """Parses proprietary 'Sens' binary accelerometer files.

    This parser handles custom binary files containing 48-bit timestamps (milliseconds)
    and 16-bit Big-Endian accelerometer readings. It supports loading data from
    both physical files on disk and in-memory byte buffers.

    Attributes:
        normalize (bool): Controls data normalization.
            If `True` (default), converts raw integer counts to physical
            acceleration units (*g*) using the factor `-4/512`.
            If `False`, returns the raw sensor counts cast to float.
    """

    normalize: bool = True

    def _read(
        self,
        obj: Path | bytes,
        func: Callable,
    ) -> pd.DataFrame:
        """Internal helper to parse binary data using a numpy reader function.

        Decodes the 48-bit timestamp by interpreting 6 bytes as a sequence of
        powers of 256.

        Args:
            obj (Path | bytes): The source to read from (file path or bytes).
            func (Callable): The numpy function to use (`fromfile` or `frombuffer`).

        Returns:
            pd.DataFrame: The parsed DataFrame with a datetime index.
        """
        data = func(obj, dtype=DTYPE, count=-1, offset=0)
        timestamps = np.dot(data["timestamp"], [1 << 40, 1 << 32, 1 << 24, 1 << 16, 1 << 8, 1])

        df = pd.DataFrame(
            {
                "datetime": pd.to_datetime(timestamps, unit="ms", utc=True),
                "acc_x": data["x"].astype(np.int16),
                "acc_y": data["y"].astype(np.int16),
                "acc_z": data["z"].astype(np.int16),
            }
        )

        self.check_empty(df)

        df.set_index("datetime", inplace=True)

        if self.normalize:
            df = df * SENS_NORMALIZATION_FACTOR

        return df.astype(np.float32)

    def from_bin(self, path: str | Path) -> pd.DataFrame:
        """Parses a Sens binary file from disk.

        Args:
            path (str | Path): The system path to the binary file.

        Returns:
            pd.DataFrame: Standardized accelerometer data.
                *Note:* If `self.normalize` is True, units are *g*.
                Otherwise, units are raw ADC counts.

        Raises:
            FileNotFoundError: If the file path does not exist.
            ValueError: If the file is empty or corrupted.
        """
        if isinstance(path, str):
            path = Path(path)

        self.check_file(path, ".bin")

        return self._read(path, np.fromfile)

    def from_buffer(self, buffer: bytes | bytearray) -> pd.DataFrame:
        """Parses Sens binary data directly from an in-memory buffer.

        Useful for processing data received over network streams or extracted
        from larger container files without writing to disk.

        Args:
            buffer (bytes | bytearray): The raw binary data.

        Returns:
            pd.DataFrame: Standardized accelerometer data.
                See [FileParser][.parser.FileParser] for column specification.

        Raises:
            TypeError: If the input is not a `bytes` or `bytearray` object.
            ValueError: If the buffer is empty or content is invalid.
        """
        if not isinstance(buffer, (bytes, bytearray)):
            raise TypeError("Expected a bytes or bytearray object.")

        return self._read(buffer, np.frombuffer)
