"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec


class UserFlag(BinaryModel):
    """
    Model representing a user flag of a PEX file.
    """

    name_index: int
    """uint16: Index(base 0) into string table."""

    flag_index: int
    """uint8: Bit index."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        name_index: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        flag_index: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)

        return cls(name_index=name_index, flag_index=flag_index)

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.name_index, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.flag_index, IntegerCodec.IntType.UInt8, output)
