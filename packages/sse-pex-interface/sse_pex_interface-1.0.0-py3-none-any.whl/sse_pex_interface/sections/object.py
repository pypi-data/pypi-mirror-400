"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec
from .object_data import ObjectData


class Object(BinaryModel):
    """
    Model representing an object from a PEX file.
    """

    name_index: int
    """uint16: Index(base 0) into string table."""

    size: int
    """uint32: Size of the following data block."""

    data: ObjectData
    """bytes[size-4]: Object data. Size includes itself for some reason, hence size-4."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        name_index: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        size: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt32)
        data: ObjectData = ObjectData.parse(stream)

        return cls(name_index=name_index, size=size, data=data)

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.name_index, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.size, IntegerCodec.IntType.UInt32, output)
        self.data.dump(output)
