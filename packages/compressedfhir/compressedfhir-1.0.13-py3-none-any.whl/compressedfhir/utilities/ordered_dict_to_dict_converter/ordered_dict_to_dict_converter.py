from typing import OrderedDict, cast


class OrderedDictToDictConverter:
    @staticmethod
    def convert[K, V](ordered_dict: OrderedDict[K, V]) -> dict[K, V]:
        """
        Converts an OrderedDict to a regular dict in a recursive manner.


        :param ordered_dict: The OrderedDict to convert
        :return: A regular dict with the same key-value pairs
        """

        def _convert[T](value: T) -> T:
            if isinstance(value, OrderedDict):
                return cast(T, {k: _convert(v) for k, v in value.items()})
            elif isinstance(value, dict):
                return cast(T, {k: _convert(v) for k, v in value.items()})
            elif isinstance(value, list):
                return cast(T, [_convert(item) for item in value])
            return value

        return _convert(ordered_dict)
