import dataclasses
import json
import uuid
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Optional, List

import pytest

from compressedfhir.utilities.fhir_json_encoder import FhirJSONEncoder

# Optional: Import for additional type support
try:
    import ipaddress
except ImportError:
    ipaddress = None  # type:ignore[assignment]


# Test support classes and enums
class TestEnum(Enum):
    OPTION1 = "value1"
    OPTION2 = "value2"


@dataclasses.dataclass
class TestDataclass:
    name: str
    age: int
    optional_field: Optional[str] = None


class TestClassWithToDict:
    # noinspection PyMethodMayBeStatic
    def to_dict(self) -> dict[str, str]:
        return {"key": "value"}


def test_fhir_json_encoder_dataclass() -> None:
    """Test serialization of dataclass"""
    test_obj = TestDataclass(name="John", age=30)
    encoded = json.dumps(test_obj, cls=FhirJSONEncoder)
    decoded = json.loads(encoded)

    assert decoded == {"name": "John", "age": 30, "optional_field": None}


def test_fhir_json_encoder_enum() -> None:
    """Test serialization of Enum"""
    encoded = json.dumps(TestEnum.OPTION1, cls=FhirJSONEncoder)
    assert encoded == '"value1"'


def test_fhir_json_encoder_decimal() -> None:
    """Test Decimal conversion"""
    # Whole number Decimal
    whole_decimal = Decimal("10")
    encoded_whole = json.dumps(whole_decimal, cls=FhirJSONEncoder)
    assert encoded_whole == "10"

    # Decimal with fractional part
    frac_decimal = Decimal("10.5")
    encoded_frac = json.dumps(frac_decimal, cls=FhirJSONEncoder)
    assert encoded_frac == "10.5"


def test_fhir_json_encoder_bytes() -> None:
    """Test bytes conversion"""
    test_bytes = b"hello world"
    encoded = json.dumps(test_bytes, cls=FhirJSONEncoder)
    assert encoded == '"hello world"'


def test_fhir_json_encoder_datetime() -> None:
    """Test datetime serialization"""
    test_datetime = datetime(2023, 1, 15, 12, 30, 45)
    encoded = json.dumps(test_datetime, cls=FhirJSONEncoder)
    assert encoded == '"2023-01-15T12:30:45"'


def test_fhir_json_encoder_date() -> None:
    """Test date serialization"""
    test_date = date(2023, 1, 15)
    encoded = json.dumps(test_date, cls=FhirJSONEncoder)
    assert encoded == '"2023-01-15"'


def test_fhir_json_encoder_time() -> None:
    """Test time serialization"""
    test_time = time(12, 30, 45)
    encoded = json.dumps(test_time, cls=FhirJSONEncoder)
    assert encoded == '"12:30:45"'


def test_fhir_json_encoder_to_dict() -> None:
    """Test objects with to_dict method"""
    test_obj = TestClassWithToDict()
    encoded = json.dumps(test_obj, cls=FhirJSONEncoder)
    assert encoded == '{"key": "value"}'


def test_fhir_json_encoder_unsupported_type() -> None:
    """Test fallback for unsupported types"""

    class UnsupportedType:
        __slots__: List[str] = []

    with pytest.raises(TypeError):
        json.dumps(UnsupportedType(), cls=FhirJSONEncoder)


def test_extended_json_encoder_uuid() -> None:
    """Test UUID serialization"""
    test_uuid = uuid.uuid4()
    encoded = json.dumps(test_uuid, cls=FhirJSONEncoder)
    assert isinstance(json.loads(encoded), str)
    assert len(json.loads(encoded)) == 36  # Standard UUID string length


def test_extended_json_encoder_set() -> None:
    """Test set and frozenset serialization"""
    test_set = {1, 2, 3}
    test_frozenset = frozenset([4, 5, 6])

    encoded_set = json.dumps(test_set, cls=FhirJSONEncoder)
    encoded_frozenset = json.dumps(test_frozenset, cls=FhirJSONEncoder)

    decoded_set = json.loads(encoded_set)
    decoded_frozenset = json.loads(encoded_frozenset)

    assert set(decoded_set) == test_set
    assert set(decoded_frozenset) == test_frozenset


def test_extended_json_encoder_complex() -> None:
    """Test complex number serialization"""
    test_complex = 3 + 4j
    encoded = json.dumps(test_complex, cls=FhirJSONEncoder)
    decoded = json.loads(encoded)

    assert decoded == {"real": 3.0, "imag": 4.0}


def test_extended_json_encoder_path() -> None:
    """Test Path object serialization"""
    test_path = Path("/test/path")
    encoded = json.dumps(test_path, cls=FhirJSONEncoder)
    assert json.loads(encoded) == str(test_path)


def test_extended_json_encoder_ip_address() -> None:
    """Test IP Address serialization (if ipaddress module is available)"""
    if ipaddress:
        ipv4 = ipaddress.IPv4Address("192.168.0.1")
        ipv6 = ipaddress.IPv6Address("2001:0db8:85a3:0000:0000:8a2e:0370:7334")

        encoded_ipv4 = json.dumps(ipv4, cls=FhirJSONEncoder)
        encoded_ipv6 = json.dumps(ipv6, cls=FhirJSONEncoder)

        assert json.loads(encoded_ipv4) == str(ipv4)
        assert json.loads(encoded_ipv6) == str(ipv6)


def test_extended_json_encoder_custom_object() -> None:
    """Test custom object serialization"""

    class CustomObject:
        def __init__(self) -> None:
            self.x = 1
            self.y = 2

    obj = CustomObject()
    encoded = json.dumps(obj, cls=FhirJSONEncoder)
    decoded = json.loads(encoded)

    assert decoded == {"x": 1, "y": 2}
