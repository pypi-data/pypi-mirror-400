import copy
import json
from typing import Any, Optional, Dict, List, cast, OrderedDict, override

from compressedfhir.fhir.fhir_meta import FhirMeta
from compressedfhir.utilities.compressed_dict.v1.compressed_dict import (
    CompressedDict,
)
from compressedfhir.utilities.compressed_dict.v1.compressed_dict_storage_mode import (
    CompressedDictStorageMode,
)
from compressedfhir.utilities.fhir_json_encoder import FhirJSONEncoder
from compressedfhir.utilities.json_helpers import FhirClientJsonHelpers


class FhirResource(CompressedDict[str, Any]):
    """
    FhirResource is a class that represents a FHIR resource.
    """

    __slots__ = CompressedDict.__slots__

    def __init__(
        self,
        initial_dict: Dict[str, Any] | OrderedDict[str, Any] | None = None,
        *,
        meta: Optional[FhirMeta] = None,
        storage_mode: CompressedDictStorageMode | None = None,
        properties_to_cache: Optional[List[str]] = None,
    ) -> None:
        if storage_mode is None:
            storage_mode = CompressedDictStorageMode.default()
        if meta is not None:
            initial_dict = initial_dict or {}
            initial_dict["meta"] = meta.dict()
        super().__init__(
            initial_dict=initial_dict,
            storage_mode=storage_mode,
            properties_to_cache=properties_to_cache or ["resourceType", "id", "meta"],
        )

    @classmethod
    def construct(cls, **kwargs: Any) -> "FhirResource":
        """
        Constructs a FhirResource object from keyword arguments.

        :param kwargs: Keyword arguments to initialize the resource.
        :return: A FhirResource object.
        """
        return cls(initial_dict=kwargs)

    @property
    def resource_type(self) -> Optional[str]:
        """Get the resource type from the resource dictionary."""
        return self.get("resourceType")

    @property
    def resource_type_and_id(self) -> Optional[str]:
        """Get the resource type and ID from the resource dictionary."""
        return (
            f"{self.resource_type}/{self.id}"
            if self.resource_type and self.id
            else None
        )

    def __deepcopy__(self, memo: Dict[int, Any]) -> "FhirResource":
        """Create a copy of the resource."""
        return FhirResource(
            initial_dict=super().raw_dict(),
            storage_mode=self._storage_mode,
        )

    def __repr__(self) -> str:
        """Custom string representation for debugging."""
        return f"FhirResource({self.resource_type}/{self.id})"

    def copy(self) -> "FhirResource":
        """
        Creates a copy of the BundleEntry object.

        :return: A new BundleEntry object with the same attributes.
        """
        return copy.deepcopy(self)

    @property
    def id(self) -> Optional[str]:
        """Get the ID from the resource dictionary."""
        return self.get("id")

    @id.setter
    def id(self, value: Optional[str]) -> None:
        """Set the ID of the Bundle."""
        self["id"] = value

    @property
    def meta(self) -> FhirMeta | None:
        """Get the meta information from the resource dictionary."""
        return (
            FhirMeta.from_dict(cast(Dict[str, Any], self.get("meta")))
            if "meta" in self
            else None
        )

    @meta.setter
    def meta(self, value: FhirMeta | None) -> None:
        """Set the meta information of the resource."""
        if value is None:
            self.pop("meta", None)
        else:
            assert isinstance(value, FhirMeta)
            self["meta"] = value.dict()

    @classmethod
    @override
    def from_json(cls, json_str: str) -> "FhirResource":
        """
        Creates a FhirResource object from a JSON string.

        :param json_str: JSON string representing the resource.
        :return: A FhirResource object.
        """
        return cast(FhirResource, super().from_json(json_str=json_str))

    @classmethod
    @override
    def from_dict(
        cls,
        d: Dict[str, Any],
        *,
        storage_mode: CompressedDictStorageMode | None = None,
        properties_to_cache: List[str] | None = None,
    ) -> "FhirResource":
        """
        Creates a FhirResource object from a dictionary.

        :param d: Dictionary representing the resource.
        :param storage_mode: Storage mode for the CompressedDict.
        :param properties_to_cache: List of properties to cache.
        :return: A FhirResource object.
        """
        if storage_mode is None:
            storage_mode = CompressedDictStorageMode.default()
        return cast(
            FhirResource,
            super().from_dict(
                d=d,
                storage_mode=storage_mode,
                properties_to_cache=properties_to_cache,
            ),
        )

    @override
    def json(self) -> str:
        """Convert the resource to a JSON string."""

        # working_dict preserves the python types so create a fhir friendly version
        raw_dict: OrderedDict[str, Any] = self.raw_dict()

        raw_dict = FhirClientJsonHelpers.remove_empty_elements_from_ordered_dict(
            raw_dict
        )
        return json.dumps(obj=raw_dict, cls=FhirJSONEncoder)

    def to_fhir_dict(self) -> Dict[str, Any]:
        """
        Convert the resource to a FHIR-compliant dictionary.

        :return: A dictionary representation of the resource.
        """
        return cast(Dict[str, Any], json.loads(self.json()))
