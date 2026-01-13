import dataclasses
import json
import uuid
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

# Optional: Import for additional type support
try:
    import ipaddress
except ImportError:
    ipaddress = None  # type:ignore[assignment]


class FhirJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        # Existing type handlers
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # type:ignore[arg-type]

        if isinstance(o, Enum):
            return o.value

        if isinstance(o, Decimal):
            # Custom Decimal conversion
            if o == o.to_integral_value():
                return int(o)
            else:
                return float(o)

        if isinstance(o, bytes):
            return o.decode("utf-8")

        if isinstance(o, (datetime, date)):
            return o.isoformat()

        if isinstance(o, time):
            return o.isoformat()

        if hasattr(o, "to_dict"):
            return o.to_dict()

        # New type handlers

        # UUID handling
        if isinstance(o, uuid.UUID):
            return str(o)

        # Set and frozenset handling
        if isinstance(o, (set, frozenset)):
            return list(o)

        # Complex number handling
        if isinstance(o, complex):
            return {"real": o.real, "imag": o.imag}

        # Path-like objects
        if isinstance(o, (Path, Path)):
            return str(o)

        # IP Address handling (if ipaddress module is available)
        if ipaddress and isinstance(o, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            return str(o)

        # Custom object serialization fallback
        if hasattr(o, "__dict__"):
            return o.__dict__

        return super().default(o)
