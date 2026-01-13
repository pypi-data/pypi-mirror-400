import zlib
from typing import Union, Optional


class StringCompressor:
    """
    A utility class for compressing and decompressing strings using zlib.

    Provides methods to compress strings to bytes and decompress bytes back to strings.
    Uses UTF-8 encoding and zlib's best compression level.
    """

    @staticmethod
    def compress(text: str, encoding: str = "utf-8") -> bytes:
        """
        Compress a given string to bytes using zlib.

        Args:
            text (str): The input string to compress
            encoding (str, optional): The encoding to use. Defaults to 'utf-8'

        Returns:
            bytes: Compressed representation of the input string

        Raises:
            TypeError: If input is not a string
            zlib.error: If compression fails
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")

        try:
            # Encode string to bytes, then compress with best compression
            return zlib.compress(text.encode(encoding), level=zlib.Z_BEST_COMPRESSION)
        except Exception as e:
            raise zlib.error(f"Compression failed: {e}")

    @staticmethod
    def decompress(
        compressed_data: Union[bytes, bytearray], encoding: str = "utf-8"
    ) -> str:
        """
        Decompress bytes back to the original string.

        Args:
            compressed_data (Union[bytes, bytearray]): Compressed data to decompress
            encoding (str, optional): The encoding to use. Defaults to 'utf-8'

        Returns:
            str: Decompressed original string

        Raises:
            TypeError: If input is not bytes or bytearray
            zlib.error: If decompression fails
        """
        if not isinstance(compressed_data, (bytes, bytearray)):
            raise TypeError("Input must be bytes or bytearray")

        try:
            # Decompress bytes, then decode to string
            return zlib.decompress(compressed_data).decode(encoding)
        except Exception as e:
            raise zlib.error(f"Decompression failed: {e}")

    @classmethod
    def compress_safe(
        cls, text: Optional[str], encoding: str = "utf-8"
    ) -> Optional[bytes]:
        """
        Safely compress a string, handling None input.

        Args:
            text (Optional[str]): The input string to compress
            encoding (str, optional): The encoding to use. Defaults to 'utf-8'

        Returns:
            Optional[bytes]: Compressed bytes or None if input is None
        """
        if text is None:
            return None
        return cls.compress(text, encoding)

    @classmethod
    def decompress_safe(
        cls, compressed_data: Optional[Union[bytes, bytearray]], encoding: str = "utf-8"
    ) -> Optional[str]:
        """
        Safely decompress bytes, handling None input.

        Args:
            compressed_data (Optional[Union[bytes, bytearray]]): Compressed data to decompress
            encoding (str, optional): The encoding to use. Defaults to 'utf-8'

        Returns:
            Optional[str]: Decompressed string or None if input is None
        """
        if compressed_data is None:
            return None
        return cls.decompress(compressed_data, encoding)
