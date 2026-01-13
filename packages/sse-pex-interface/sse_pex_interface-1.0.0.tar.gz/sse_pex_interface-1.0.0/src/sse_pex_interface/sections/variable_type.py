"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec


class VariableType(BinaryModel):
    """
    Model representing a variable type of a PEX file.
    """

    name: int
    """uint16: Index(base 0) into string table."""

    type: int
    """uint16: Index(base 0) into string table."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        name: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        type: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)

        return cls(name=name, type=type)

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.name, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.type, IntegerCodec.IntType.UInt16, output)
