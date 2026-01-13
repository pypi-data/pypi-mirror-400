from abc import ABC, abstractmethod

import msgspec

__all__ = (
    "AbstractJSONDecoder",
    "MSGSpecDecoder",
)


class AbstractJSONDecoder(ABC):
    """JSON decoder interface"""

    @staticmethod
    @abstractmethod
    def serialize[T](data: bytes, model: type[T]) -> T:
        """Serializes a raw bytes object into a given data structure model
        :param data: Raw bytes to serialize
        :param model: Model used for serialization
        :return: Serialized instance of a given model
        """


class MSGSpecDecoder(AbstractJSONDecoder):
    """JSON decoder that uses the msgspec library"""

    @staticmethod
    def serialize[T: msgspec.Struct](data: bytes, model: type[T]) -> T:
        """Serializes a raw bytes object into a given data structure model
        :param data: Raw bytes to serialize
        :param model: Model used for serialization
        :return: Serialized instance of a given model
        """
        return msgspec.json.decode(data, type=model)
