import logging
from collections import OrderedDict
from datetime import datetime, date, time
from decimal import Decimal
from logging import Logger
from typing import Any, Dict, Callable, Optional, Union, cast, List
from zoneinfo import ZoneInfo


class TypePreservationDecoder:
    """
    Advanced JSON decoder for complex type reconstruction with nested type support
    """

    @classmethod
    def decode(
        cls,
        dct: Union[str, Dict[str, Any], List[Any]],
        custom_decoders: Optional[Dict[str, Callable[[Any], Any]]] = None,
        use_ordered_dict: bool = True,
    ) -> Any:
        """
        Decode complex types, including nested datetime fields

        Args:
            dct: Dictionary to decode
            custom_decoders: Optional additional custom decoders
            use_ordered_dict: Flag to control whether to use OrderedDict or not

        Returns:
            Reconstructed object or original dictionary
        """
        logger: Logger = logging.getLogger(__name__)

        # Default decoders for built-in types with nested support
        def datetime_decoder(d: Union[str, Dict[str, Any]]) -> datetime:
            if isinstance(d, str):
                return datetime.fromisoformat(d)
            elif isinstance(d, dict) and "iso" in d:
                return datetime.fromisoformat(d["iso"])
            return cast(datetime, d)

        def date_decoder(d: Union[str, Dict[str, Any]]) -> date:
            if isinstance(d, str):
                return date.fromisoformat(d)
            elif isinstance(d, dict) and "iso" in d:
                return date.fromisoformat(d["iso"])
            return cast(date, d)

        def time_decoder(d: Union[str, Dict[str, Any]]) -> time:
            if isinstance(d, str):
                return time.fromisoformat(d)
            elif isinstance(d, dict) and "iso" in d:
                # Extract ISO time string
                iso_time: str = d["iso"]

                # Parse time from ISO format
                parsed_time = time.fromisoformat(iso_time)

                # Add timezone if specified
                tz_info = d.get("tzinfo")
                if tz_info:
                    try:
                        tz_aware_time = parsed_time.replace(tzinfo=ZoneInfo(tz_info))
                        return tz_aware_time
                    except Exception as e:
                        raise ValueError(f"Invalid timezone: {tz_info}") from e
                else:
                    # If no timezone info, return naive time
                    return parsed_time
            return cast(time, d)

        default_decoders: Dict[str, Callable[[Any], Any]] = {
            "datetime": datetime_decoder,
            "date": date_decoder,
            "time": time_decoder,
            "decimal": lambda d: Decimal(d["value"] if isinstance(d, dict) else d),
            "complex": lambda d: complex(d["real"], d["imag"])
            if isinstance(d, dict)
            else d,
            "bytes": lambda d: d["value"].encode("latin-1")
            if isinstance(d, dict)
            else d,
            "set": lambda d: set(d["values"]) if isinstance(d, dict) else d,
        }

        # Merge custom decoders with default decoders
        decoders = {**default_decoders, **(custom_decoders or {})}

        # Recursively decode nested structures
        def recursive_decode(value: Any) -> Any:
            if isinstance(value, dict):
                # Check for type marker in the dictionary
                if "__type__" in value:
                    type_name = value["__type__"]

                    # Handle built-in type decoders
                    if type_name in decoders:
                        return decoders[type_name](value)

                    # Handle custom object reconstruction
                    if "__module__" in value and "attributes" in value:
                        try:
                            # Dynamically import the class
                            module = __import__(
                                value["__module__"], fromlist=[type_name]
                            )
                            cls_ = getattr(module, type_name)

                            # Create instance and set attributes with recursive decoding
                            obj = cls_.__new__(cls_)
                            obj.__dict__.update(
                                {
                                    k: recursive_decode(v)
                                    for k, v in value["attributes"].items()
                                }
                            )
                            return obj
                        except (ImportError, AttributeError) as e:
                            logger.error(f"Could not reconstruct {type_name}: {e}")
                            return value

                # Recursively decode dictionary values
                # Conditionally use OrderedDict or regular dict
                dict_type = OrderedDict if use_ordered_dict else dict
                return dict_type((k, recursive_decode(v)) for k, v in value.items())

            # Recursively decode list or tuple
            elif isinstance(value, (list, tuple)):
                return type(value)(recursive_decode(item) for item in value)

            return value

        # Start recursive decoding
        return recursive_decode(dct)
