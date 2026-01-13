from datetime import datetime

import pytest
from typing import Any, cast

from compressedfhir.utilities.compressed_dict.v1.compressed_dict import (
    CompressedDict,
)
from compressedfhir.utilities.compressed_dict.v1.compressed_dict_access_error import (
    CompressedDictAccessError,
)
from compressedfhir.utilities.compressed_dict.v1.compressed_dict_storage_mode import (
    CompressedDictStorageMode,
    CompressedDictStorageType,
)


class TestCompressedDict:
    def test_init_empty(self) -> None:
        """Test initialization with no initial data"""
        cd: CompressedDict[str, Any] = CompressedDict(
            storage_mode=CompressedDictStorageMode(storage_type="raw"),
            properties_to_cache=[],
        )
        assert len(cd) == 0
        assert cd._storage_mode.storage_type == "raw"

    def test_init_with_dict(self) -> None:
        """Test initialization with initial dictionary"""
        initial_data = {"a": 1, "b": 2, "c": 3}
        cd = CompressedDict(
            initial_dict=initial_data,
            storage_mode=CompressedDictStorageMode(storage_type="raw"),
            properties_to_cache=[],
        )

        with cd.transaction():
            assert len(cd) == 3
            assert cd["a"] == 1
            assert cd["b"] == 2
            assert cd["c"] == 3

    @pytest.mark.parametrize("storage_type", ["raw", "msgpack", "compressed_msgpack"])
    def test_storage_modes(self, storage_type: CompressedDictStorageType) -> None:
        """Test different storage modes"""
        initial_data = {"key": "value"}
        cd = CompressedDict(
            initial_dict=initial_data,
            storage_mode=CompressedDictStorageMode(storage_type=storage_type),
            properties_to_cache=[],
        )
        assert cd._storage_mode.storage_type == storage_type
        with cd.transaction():
            assert cd["key"] == "value"

    def test_setitem_and_getitem(self) -> None:
        """Test setting and getting items"""
        cd: CompressedDict[str, Any] = CompressedDict(
            storage_mode=CompressedDictStorageMode(storage_type="compressed_msgpack"),
            properties_to_cache=[],
        )
        with cd.transaction():
            cd["key1"] = "value1"
            cd["key2"] = 42
            cd["key3"] = {"nested": "dict"}

        with cd.transaction():
            assert cd["key1"] == "value1"
            assert cd["key2"] == 42
            assert cd["key3"] == {"nested": "dict"}

    def test_delitem(self) -> None:
        """Test deleting items"""
        cd = CompressedDict(
            initial_dict={"a": 1, "b": 2},
            storage_mode=CompressedDictStorageMode(storage_type="compressed_msgpack"),
            properties_to_cache=[],
        )
        with cd.transaction():
            del cd["a"]

        with cd.transaction():
            assert len(cd) == 1

        with cd.transaction():
            assert not cd.__contains__("a")
            assert "a" not in cd
            assert "b" in cd

    def test_contains(self) -> None:
        """Test key existence checks"""
        cd = CompressedDict(
            initial_dict={"a": 1, "b": 2},
            storage_mode=CompressedDictStorageMode(),
            properties_to_cache=[],
        )

        with cd.transaction():
            assert "a" in cd
            assert "b" in cd
            assert "c" not in cd

    def test_keys_and_values(self) -> None:
        """Test keys and values methods"""
        initial_data = {"a": 1, "b": 2, "c": 3}
        cd: CompressedDict[str, int] = CompressedDict(
            initial_dict=initial_data,
            storage_mode=CompressedDictStorageMode(),
            properties_to_cache=[],
        )

        with cd.transaction():
            assert set(cd.keys()) == {"a", "b", "c"}
            assert set(cd.values()) == {1, 2, 3}

    def test_items(self) -> None:
        """Test items method"""
        initial_data = {"a": 1, "b": 2, "c": 3}
        cd = CompressedDict(
            initial_dict=initial_data,
            storage_mode=CompressedDictStorageMode(),
            properties_to_cache=[],
        )

        with cd.transaction():
            assert set(cd.items()) == {("a", 1), ("b", 2), ("c", 3)}

    def test_get_method(self) -> None:
        """Test get method with default"""
        cd: CompressedDict[str, Any] = CompressedDict(
            initial_dict={"a": 1},
            storage_mode=CompressedDictStorageMode(),
            properties_to_cache=[],
        )
        with cd.transaction():
            assert cd.get("a") == 1
            assert cd.get("b") is None
            assert cd.get("b", "default") == "default"

    def test_to_dict(self) -> None:
        """Test conversion to standard dictionary"""
        initial_data = {"a": 1, "b": 2}
        cd = CompressedDict(
            initial_dict=initial_data,
            storage_mode=CompressedDictStorageMode(),
            properties_to_cache=[],
        )

        with cd.transaction():
            assert cd.dict() == initial_data

    def test_complex_nested_structures(self) -> None:
        """Test storage of complex nested structures"""
        complex_data = {
            "nested_dict": {"inner_key": "inner_value"},
            "list": [1, 2, 3],
            "mixed": [{"a": 1}, 2, "three"],
        }

        # Test each storage storage_type
        for storage_type in ["raw", "msgpack", "compressed_msgpack"]:
            cd = CompressedDict(
                initial_dict=complex_data,
                storage_mode=CompressedDictStorageMode(
                    storage_type=cast(CompressedDictStorageType, storage_type)
                ),
                properties_to_cache=[],
            )
            with cd.transaction():
                assert cd["nested_dict"] == {"inner_key": "inner_value"}
                assert cd["list"] == [1, 2, 3]
                assert cd["mixed"] == [{"a": 1}, 2, "three"]

    def test_repr(self) -> None:
        """Test string representation"""
        cd = CompressedDict(
            initial_dict={"a": 1, "b": 2},
            storage_mode=CompressedDictStorageMode(),
            properties_to_cache=[],
        )
        repr_str = repr(cd)

        assert repr_str == "CompressedDict(storage_type='compressed', keys=2)"

    def test_error_handling(self) -> None:
        """Test error scenarios"""
        cd: CompressedDict[str, Any] = CompressedDict(
            storage_mode=CompressedDictStorageMode(), properties_to_cache=[]
        )

        # Test KeyError
        with pytest.raises(KeyError):
            with cd.transaction():
                _ = cd["non_existent_key"]

    @pytest.mark.parametrize("storage_type", ["raw", "msgpack", "compressed_msgpack"])
    def test_large_data_handling(self, storage_type: CompressedDictStorageType) -> None:
        """Test handling of large datasets"""
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}

        cd = CompressedDict(
            initial_dict=large_data,
            storage_mode=CompressedDictStorageMode(storage_type=storage_type),
            properties_to_cache=[],
        )

        assert len(cd) == 1000
        with cd.transaction():
            assert cd["key_500"] == "value_500"


def test_transaction_basic_raw_storage() -> None:
    """
    Test basic transaction functionality with raw storage mode
    """
    storage_mode = CompressedDictStorageMode(storage_type="raw")
    initial_dict = {"key1": "value1", "key2": "value2"}

    compressed_dict = CompressedDict(
        initial_dict=initial_dict, storage_mode=storage_mode, properties_to_cache=None
    )

    # Verify initial state
    assert compressed_dict._transaction_depth == 0

    # Use transaction context
    with compressed_dict.transaction() as d:
        assert compressed_dict._transaction_depth == 1
        assert d._working_dict is not None
        assert d._working_dict == initial_dict

        # Modify the dictionary
        d["key3"] = "value3"

    # After transaction
    assert compressed_dict._transaction_depth == 0
    assert compressed_dict.raw_dict() == {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }


def test_transaction_nested_context() -> None:
    """
    Test nested transaction contexts
    """
    storage_mode = CompressedDictStorageMode(storage_type="msgpack")
    initial_dict = {"key1": "value1"}

    compressed_dict = CompressedDict(
        initial_dict=initial_dict, storage_mode=storage_mode, properties_to_cache=None
    )

    with compressed_dict.transaction():
        assert compressed_dict._transaction_depth == 1

        with compressed_dict.transaction():
            assert compressed_dict._transaction_depth == 2
            compressed_dict["key2"] = "value2"

        assert compressed_dict._transaction_depth == 1

    assert compressed_dict._transaction_depth == 0
    assert compressed_dict.raw_dict() == {"key1": "value1", "key2": "value2"}


def test_transaction_access_error() -> None:
    """
    Test that accessing or modifying dictionary outside transaction raises an error
    """
    storage_mode = CompressedDictStorageMode(storage_type="compressed_msgpack")
    compressed_dict = CompressedDict(
        initial_dict={"key1": "value1"},
        storage_mode=storage_mode,
        properties_to_cache=None,
    )

    # Test getdict outside transaction
    with pytest.raises(CompressedDictAccessError):
        compressed_dict._get_dict()

    # Test __getitem__ outside transaction
    with pytest.raises(CompressedDictAccessError):
        _ = compressed_dict["key1"]

    # Test __setitem__ outside transaction
    with pytest.raises(CompressedDictAccessError):
        compressed_dict["key2"] = "value2"


def test_transaction_different_storage_modes() -> None:
    """
    Test transaction with different storage modes
    """
    storage_modes = [
        CompressedDictStorageMode(storage_type="raw"),
        CompressedDictStorageMode(storage_type="msgpack"),
        CompressedDictStorageMode(storage_type="compressed_msgpack"),
    ]

    for storage_mode in storage_modes:
        initial_dict = {"key1": "value1"}

        compressed_dict = CompressedDict(
            initial_dict=initial_dict,
            storage_mode=storage_mode,
            properties_to_cache=None,
        )

        with compressed_dict.transaction() as d:
            d["key2"] = "value2"

        assert compressed_dict.raw_dict() == {"key1": "value1", "key2": "value2"}


def test_transaction_with_properties_to_cache() -> None:
    """
    Test transaction with properties to cache
    """
    storage_mode = CompressedDictStorageMode(storage_type="raw")
    initial_dict = {"key1": "value1", "important_prop": "cached_value"}

    compressed_dict = CompressedDict(
        initial_dict=initial_dict,
        storage_mode=storage_mode,
        properties_to_cache=["important_prop"],
    )

    with compressed_dict.transaction() as d:
        d["key2"] = "value2"

    assert compressed_dict.raw_dict() == {
        "key1": "value1",
        "important_prop": "cached_value",
        "key2": "value2",
    }
    assert compressed_dict._cached_properties == {"important_prop": "cached_value"}


def test_transaction_error_handling() -> None:
    """
    Test error handling during transaction
    """
    storage_mode = CompressedDictStorageMode(storage_type="compressed")
    compressed_dict = CompressedDict(
        initial_dict={"key1": "value1"},
        storage_mode=storage_mode,
        properties_to_cache=None,
    )

    try:
        with compressed_dict.transaction():
            compressed_dict["key2"] = "value2"
            raise ValueError("Simulated error")
    except ValueError:
        # Ensure transaction depth is reset even after an error
        assert compressed_dict._transaction_depth == 0

        # Verify the dictionary state remains unchanged
        with compressed_dict.transaction() as d:
            assert d.dict() == {"key1": "value1", "key2": "value2"}


def test_nested_dict_with_datetime() -> None:
    nested_dict = {
        "beneficiary": {"reference": "Patient/1234567890123456703", "type": "Patient"},
        "class": [
            {
                "name": "Aetna Plan",
                "type": {
                    "coding": [
                        {
                            "code": "plan",
                            "display": "Plan",
                            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                        }
                    ]
                },
                "value": "AE303",
            }
        ],
        "costToBeneficiary": [
            {
                "type": {"text": "Annual Physical Exams NMC - In Network"},
                "valueQuantity": {
                    "system": "http://aetna.com/Medicare/CostToBeneficiary/ValueQuantity/code",
                    "unit": "$",
                    "value": 50.0,
                },
            }
        ],
        "id": "3456789012345670304",
        "identifier": [
            {
                "system": "https://sources.aetna.com/coverage/identifier/membershipid/59",
                "type": {
                    "coding": [
                        {
                            "code": "SN",
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        }
                    ]
                },
                "value": "435679010300+AE303+2021-01-01",
            },
            {
                "id": "uuid",
                "system": "https://www.icanbwell.com/uuid",
                "value": "92266603-aa8b-58c6-99bd-326fd1da1896",
            },
        ],
        "meta": {
            "security": [
                {"code": "aetna", "system": "https://www.icanbwell.com/owner"},
                {"code": "aetna", "system": "https://www.icanbwell.com/access"},
                {"code": "aetna", "system": "https://www.icanbwell.com/vendor"},
                {"code": "proa", "system": "https://www.icanbwell.com/connectionType"},
            ],
            "source": "http://mock-server:1080/test_patient_access_transformer/source/4_0_0/Coverage/3456789012345670304",
        },
        "network": "Medicare - MA/NY/NJ - Full Reciprocity",
        "payor": [
            {
                "display": "Aetna",
                "reference": "Organization/6667778889990000015",
                "type": "Organization",
            }
        ],
        "period": {
            "end": datetime.fromisoformat("2021-12-31").date(),
            "start": datetime.fromisoformat("2021-01-01").date(),
        },
        "policyHolder": {"reference": "Patient/1234567890123456703", "type": "Patient"},
        "relationship": {
            "coding": [
                {
                    "code": "self",
                    "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
                }
            ]
        },
        "resourceType": "Coverage",
        "status": "active",
        "subscriber": {"reference": "Patient/1234567890123456703", "type": "Patient"},
        "subscriberId": "435679010300",
        "type": {
            "coding": [
                {
                    "code": "PPO",
                    "display": "preferred provider organization policy",
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                }
            ]
        },
    }

    compressed_dict = CompressedDict(
        initial_dict=nested_dict,
        storage_mode=CompressedDictStorageMode.compressed(),
        properties_to_cache=[],
    )

    plain_dict = compressed_dict.to_plain_dict()

    assert plain_dict["period"]["start"] == nested_dict["period"]["start"]  # type: ignore[index]
    assert plain_dict == nested_dict
