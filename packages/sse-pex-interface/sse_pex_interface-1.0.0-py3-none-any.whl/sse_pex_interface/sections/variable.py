"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec
from .variable_data import VariableData


class Variable(BinaryModel):
    """
    Model representing a variable of a PEX file.
    """

    name: int
    """uint16: Index(base 0) into string table."""

    type_name: int
    """uint16: Index(base 0) into string table."""

    user_flags: int
    """uint32: User flags."""

    data: VariableData
    """Default value."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        name: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        type_name: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        user_flags: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt32)
        data: VariableData = VariableData.parse(stream)

        return cls(name=name, type_name=type_name, user_flags=user_flags, data=data)

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.name, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.type_name, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.user_flags, IntegerCodec.IntType.UInt32, output)

        self.data.dump(output)
