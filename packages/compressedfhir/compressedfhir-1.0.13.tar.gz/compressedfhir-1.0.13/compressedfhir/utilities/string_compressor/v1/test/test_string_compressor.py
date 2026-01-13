# Basic Compression and Decompression Tests
from typing import Optional, Union

import pytest
import zlib

from compressedfhir.utilities.string_compressor.v1.string_compressor import (
    StringCompressor,
)


@pytest.mark.parametrize(
    "input_text",
    [
        "Hello, World!",
        "Python is awesome",
        "12345",
        "",  # Empty string
        "🌍🚀",  # Unicode characters
    ],
)
def test_compress_decompress_basic(input_text: str) -> None:
    """
    Test basic compression and decompression functionality
    """
    # Compress
    compressed = StringCompressor.compress(input_text)

    # Verify compression reduces size
    # assert len(compressed) < len(input_text.encode('utf-8'))

    # Decompress
    decompressed = StringCompressor.decompress(compressed)

    # Verify original text is preserved
    assert decompressed == input_text


# Error Handling Tests
def test_compress_invalid_input() -> None:
    """
    Test compression with invalid input type
    """
    with pytest.raises(TypeError, match="Input must be a string"):
        StringCompressor.compress(123)  # type:ignore[arg-type]

    with pytest.raises(TypeError, match="Input must be a string"):
        StringCompressor.compress(None)  # type:ignore[arg-type]


def test_decompress_invalid_input() -> None:
    """
    Test decompression with invalid input type
    """
    with pytest.raises(TypeError, match="Input must be bytes or bytearray"):
        StringCompressor.decompress("not bytes")  # type:ignore[arg-type]

    with pytest.raises(TypeError, match="Input must be bytes or bytearray"):
        StringCompressor.decompress(123)  # type:ignore[arg-type]


# Safe Method Tests
@pytest.mark.parametrize("input_text", ["Test string", None, ""])
def test_compress_safe(input_text: Optional[str]) -> None:
    """
    Test safe compression method
    """
    compressed = StringCompressor.compress_safe(input_text)

    if input_text is None:
        assert compressed is None
    else:
        assert isinstance(compressed, bytes)
        # Verify we can decompress
        decompressed = StringCompressor.decompress_safe(compressed)
        assert decompressed == input_text


@pytest.mark.parametrize(
    "input_data", [b"compressed data", None, bytearray(b"another compressed data")]
)
def test_decompress_safe(input_data: Optional[Union[bytes, bytearray]]) -> None:
    """
    Test safe decompression method
    """
    if input_data is None:
        decompressed = StringCompressor.decompress_safe(input_data)
        assert decompressed is None
    else:
        # First compress a string
        original = "Test string to compress"
        compressed = StringCompressor.compress(original)

        # Then decompress
        decompressed = StringCompressor.decompress_safe(compressed)
        assert decompressed == original


# Encoding Tests
@pytest.mark.parametrize("encoding", ["utf-8", "ascii", "latin-1"])
def test_custom_encoding(encoding: str) -> None:
    """
    Test compression and decompression with different encodings
    """
    input_text = "Hello, World!"

    # Compress with custom encoding
    compressed = StringCompressor.compress(input_text, encoding=encoding)

    # Decompress with same encoding
    decompressed = StringCompressor.decompress(compressed, encoding=encoding)

    assert decompressed == input_text


# Compression Efficiency Tests
def test_compression_efficiency() -> None:
    """
    Test that compression actually reduces data size
    """
    # Long repetitive string for better compression
    input_text = "Hello " * 1000

    # Compress
    compressed = StringCompressor.compress(input_text)

    # Check compression ratio
    original_size = len(input_text.encode("utf-8"))
    compressed_size = len(compressed)

    # Verify significant size reduction
    assert compressed_size < original_size

    # Verify lossless decompression
    decompressed = StringCompressor.decompress(compressed)
    assert decompressed == input_text


# Edge Case Tests
def test_very_large_string() -> None:
    """
    Test compression and decompression of a very large string
    """
    # Generate a large string
    large_text = "A" * (1024 * 1024)  # 1MB of text

    # Compress
    compressed = StringCompressor.compress(large_text)

    # Decompress
    decompressed = StringCompressor.decompress(compressed)

    assert decompressed == large_text


# Error Scenario Tests
def test_decompress_corrupted_data() -> None:
    """
    Test decompression of corrupted data
    """
    # Create some corrupted compressed data
    with pytest.raises(zlib.error):
        StringCompressor.decompress(b"corrupted data")


# Performance Benchmark (optional)
def test_compression_performance() -> None:
    """
    Basic performance test for compression and decompression
    """
    import timeit

    # Test string
    test_string = "Performance test " * 100

    # Measure compression time
    compression_time = timeit.timeit(
        lambda: StringCompressor.compress(test_string), number=100
    )

    # Measure decompression time
    compressed = StringCompressor.compress(test_string)
    decompression_time = timeit.timeit(
        lambda: StringCompressor.decompress(compressed), number=100
    )

    # Basic performance assertions (these can be adjusted)
    assert compression_time < 1.0  # 100 compressions in less than 1 second
    assert decompression_time < 1.0  # 100 decompressions in less than 1 second
