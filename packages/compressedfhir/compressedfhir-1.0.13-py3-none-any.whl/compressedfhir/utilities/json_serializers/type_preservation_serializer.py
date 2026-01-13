import json
from typing import Any, Callable, Dict

from compressedfhir.utilities.json_serializers.type_preservation_decoder import (
    TypePreservationDecoder,
)
from compressedfhir.utilities.json_serializers.type_preservation_encoder import (
    TypePreservationEncoder,
)


class TypePreservationSerializer:
    """
    Comprehensive serialization and deserialization utility
    """

    @classmethod
    def serialize(cls, data: Any, **kwargs: Any) -> str:
        """
        Serialize data with advanced type handling

        Args:
            data: Data to serialize
            kwargs: Additional JSON dumps arguments

        Returns:
            JSON string representation
        """
        return json.dumps(
            data, cls=TypePreservationEncoder, separators=(",", ":"), **kwargs
        )

    @classmethod
    def deserialize(
        cls,
        json_str: str,
        custom_decoders: Dict[str, Callable[[Any], Any]] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Deserialize JSON string with advanced type reconstruction

        Args:
            json_str: JSON string to deserialize
            custom_decoders: Optional additional custom decoders
            kwargs: Additional JSON loads arguments

        Returns:
            Reconstructed object
        """
        return json.loads(
            json_str,
            object_hook=lambda dct: TypePreservationDecoder.decode(
                dct, custom_decoders
            ),
            **kwargs,
        )
