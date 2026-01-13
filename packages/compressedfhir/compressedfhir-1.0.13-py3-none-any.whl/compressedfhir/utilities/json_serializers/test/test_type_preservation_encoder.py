import logging
from datetime import datetime, timezone, date, time
from decimal import Decimal
from logging import Logger
from typing import Type, Any
from zoneinfo import ZoneInfo

import pytest

from compressedfhir.utilities.json_serializers.type_preservation_encoder import (
    TypePreservationEncoder,
)


class TestCustomObject:
    def __init__(self, name: str, value: int):
        self.name: str = name
        self.value: int = value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TestCustomObject):
            return False
        return self.name == other.name and self.value == other.value


@pytest.mark.parametrize(
    "input_type, input_value, expected_type",
    [
        (datetime, datetime(2023, 1, 1, tzinfo=timezone.utc), "datetime"),
        (
            datetime,
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Pacific/Honolulu")),
            "datetime",
        ),
        (date, date(2023, 1, 1), "date"),
        (time, time(14, 30, 15), "time"),
        (time, time(14, 30, 15, tzinfo=ZoneInfo("Pacific/Honolulu")), "time"),
        (Decimal, Decimal("3.14"), "decimal"),
        (complex, 3 + 4j, "complex"),
        (bytes, b"test", "bytes"),
        (set, {1, 2, 3}, "set"),
    ],
)
def test_complex_type_serialization(
    input_type: Type[Any], input_value: Any, expected_type: str
) -> None:
    """
    Test serialization of various complex types
    """
    logger: Logger = logging.getLogger(__name__)
    encoder = TypePreservationEncoder()
    serialized = encoder.default(input_value)

    logger.info(serialized)
    assert isinstance(serialized, dict)
    assert serialized.get("__type__") == expected_type


# noinspection PyMethodMayBeStatic
def test_custom_object_serialization() -> None:
    """
    Test serialization of custom objects
    """
    custom_obj = TestCustomObject("test", 42)
    encoder = TypePreservationEncoder()
    serialized = encoder.default(custom_obj)

    assert isinstance(serialized, dict)
    assert serialized.get("__type__") == "TestCustomObject"
    assert serialized.get("__module__") == __name__
    assert "attributes" in serialized
