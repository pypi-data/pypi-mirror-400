import json
from collections.abc import Callable
from datetime import datetime, date, time
from decimal import Decimal
from typing import Any, Dict, Type


class TypePreservationEncoder(json.JSONEncoder):
    """
    Advanced JSON encoder for complex type serialization
    """

    TYPE_MAP: Dict[Type[Any], Callable[[Any], Any]] = {
        datetime: lambda dt: {
            "__type__": "datetime",
            "iso": dt.isoformat(),
            "tzinfo": str(dt.tzinfo) if dt.tzinfo else None,
        },
        date: lambda d: {"__type__": "date", "iso": d.isoformat()},
        time: lambda t: {
            "__type__": "time",
            "iso": t.isoformat(),
            "tzinfo": str(t.tzinfo) if t.tzinfo else None,
        },
        Decimal: lambda d: {"__type__": "decimal", "value": str(d)},
        complex: lambda c: {"__type__": "complex", "real": c.real, "imag": c.imag},
        bytes: lambda b: {"__type__": "bytes", "value": b.decode("latin-1")},
        set: lambda s: {"__type__": "set", "values": list(s)},
    }

    def default(self, obj: Any) -> Any:
        """
        Custom serialization for complex types

        Args:
            obj: Object to serialize

        Returns:
            Serializable representation of the object
        """
        # Check if the type is in our custom type map
        for type_, serializer in self.TYPE_MAP.items():
            if isinstance(obj, type_):
                return serializer(obj)

        # Handle custom objects with __dict__
        if hasattr(obj, "__dict__"):
            return {
                "__type__": obj.__class__.__name__,
                "__module__": obj.__class__.__module__,
                "attributes": obj.__dict__,
            }

        # Fallback to default JSON encoder
        return super().default(obj)
