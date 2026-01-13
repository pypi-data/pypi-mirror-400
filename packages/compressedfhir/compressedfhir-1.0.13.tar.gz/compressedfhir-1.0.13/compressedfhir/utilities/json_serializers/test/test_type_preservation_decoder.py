from datetime import datetime, date, time
from decimal import Decimal
from typing import Type, Any, Dict, Optional
import pytest

from compressedfhir.utilities.json_serializers.type_preservation_decoder import (
    TypePreservationDecoder,
)


class TestCustomObject:
    def __init__(
        self,
        name: str,
        value: int,
        created_at: Optional[datetime] = None,
        nested_data: Optional[Dict[str, Any]] = None,
    ):
        self.name: str = name
        self.value: int = value
        self.created_at: Optional[datetime] = created_at
        self.nested_data: Optional[Dict[str, Any]] = nested_data

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TestCustomObject):
            return False
        return (
            self.name == other.name
            and self.value == other.value
            and self.created_at == other.created_at
            and self.nested_data == other.nested_data
        )


@pytest.mark.parametrize(
    "input_type, input_dict, expected_type",
    [
        (
            "datetime",
            {"__type__": "datetime", "iso": "2023-01-01T00:00:00+00:00"},
            datetime,
        ),
        (
            "datetime",
            {
                "__type__": "datetime",
                "iso": "2023-01-01T00:00:00-08:00",
                "tzinfo": "Pacific/Honolulu",
            },
            datetime,
        ),
        ("date", {"__type__": "date", "iso": "2023-01-01"}, date),
        ("time", {"__type__": "time", "iso": "14:30:15"}, time),
        (
            "time",
            {"__type__": "time", "iso": "14:30:15", "tzinfo": "Pacific/Honolulu"},
            time,
        ),
        ("decimal", {"__type__": "decimal", "value": "3.14"}, Decimal),
        ("complex", {"__type__": "complex", "real": 3, "imag": 4}, complex),
        ("bytes", {"__type__": "bytes", "value": "test"}, bytes),
        ("set", {"__type__": "set", "values": [1, 2, 3]}, set),
    ],
)
def test_complex_type_decoding(
    input_type: str, input_dict: Dict[str, Any], expected_type: Type[Any]
) -> None:
    """
    Test decoding of various complex types
    """
    decoded = TypePreservationDecoder.decode(input_dict)
    assert isinstance(decoded, expected_type)


def test_custom_object_decoding() -> None:
    """
    Test decoding of custom objects
    """
    custom_obj_dict = {
        "__type__": "TestCustomObject",
        "__module__": __name__,
        "attributes": {"name": "test", "value": 42},
    }
    decoded = TypePreservationDecoder.decode(custom_obj_dict)
    assert isinstance(decoded, TestCustomObject)
    assert decoded.name == "test"
    assert decoded.value == 42


def test_custom_decoder() -> None:
    """
    Test custom decoder functionality
    """

    def custom_decoder(data: Dict[str, Any]) -> Any:
        if data.get("__type__") == "special_type":
            return f"Decoded: {data['value']}"
        return data

    special_dict = {"__type__": "special_type", "value": "test"}
    decoded = TypePreservationDecoder.decode(
        special_dict, custom_decoders={"special_type": custom_decoder}
    )
    assert decoded == "Decoded: test"


def test_nested_datetime_decoding() -> None:
    """
    Test decoding of nested datetime fields
    """
    nested_datetime_dict = {
        "__type__": "TestCustomObject",
        "__module__": __name__,
        "attributes": {
            "name": "test",
            "value": 42,
            "created_at": {"__type__": "datetime", "iso": "2023-06-15T10:30:00"},
            "nested_data": {
                "timestamp": {"__type__": "datetime", "iso": "2023-06-16T15:45:00"}
            },
        },
    }

    decoded: TestCustomObject = TypePreservationDecoder.decode(nested_datetime_dict)

    assert isinstance(decoded, TestCustomObject)
    assert decoded.name == "test"
    assert decoded.value == 42

    # Check nested datetime fields
    assert hasattr(decoded, "created_at")
    assert isinstance(decoded.created_at, datetime)
    assert decoded.created_at.year == 2023
    assert decoded.created_at.month == 6
    assert decoded.created_at.day == 15

    assert hasattr(decoded, "nested_data")
    assert isinstance(decoded.nested_data, dict)
    assert "timestamp" in decoded.nested_data
    assert isinstance(decoded.nested_data["timestamp"], datetime)
    assert decoded.nested_data["timestamp"].year == 2023
    assert decoded.nested_data["timestamp"].month == 6
    assert decoded.nested_data["timestamp"].day == 16


def test_direct_value_decoding() -> None:
    """
    Test decoding of direct values without type markers
    """
    # Test datetime direct string
    datetime_str = "2023-01-01T00:00:00"
    decoded_datetime = TypePreservationDecoder.decode(datetime_str)
    assert decoded_datetime == datetime_str

    # Test list with mixed types
    mixed_list = [
        {"__type__": "datetime", "iso": "2023-06-15T10:30:00"},
        42,
        "plain string",
    ]
    decoded_list = TypePreservationDecoder.decode(mixed_list)
    assert len(decoded_list) == 3
    assert isinstance(decoded_list[0], datetime)
    assert decoded_list[1] == 42
    assert decoded_list[2] == "plain string"
