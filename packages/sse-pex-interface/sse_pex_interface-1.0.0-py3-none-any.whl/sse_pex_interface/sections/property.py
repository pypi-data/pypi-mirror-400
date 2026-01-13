"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Optional, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec
from .function import Function


class Property(BinaryModel):
    """
    Model for a property of a PEX file.
    """

    name: int
    """uint16: Index(base 0) into string table."""

    type: int
    """uint16: Index(base 0) into string table."""

    docstring: int
    """uint16: Index(base 0) into string table."""

    user_flags: int
    """uint32: User flags."""

    flags: int
    """
    uint8: Flags.

    - bit 1 = read
    - bit 2 = write
    - bit 3 = autovar

    For example, Property in a source script contains only get() or is defined
    AutoReadOnly then the flags is 0x1, contains get() and set() then the flags is 0x3.
    """

    auto_var_name: Optional[int]
    """uint16: Index(base 0) into string table, present if `(flags & 4) != 0`."""

    read_handler: Optional[Function]
    """Function, present if `(flags & 5) == 1`."""

    write_handler: Optional[Function]
    """Function, present if `(flags & 6) == 2`."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        name: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        type: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        docstring: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        user_flags: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt32)
        flags: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)

        auto_var_name: Optional[int] = None
        read_handler: Optional[Function] = None
        write_handler: Optional[Function] = None

        if (flags & 4) != 0:
            auto_var_name = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)

        if (flags & 5) == 1:
            read_handler = Function.parse(stream)

        if (flags & 6) == 2:
            write_handler = Function.parse(stream)

        return cls(
            name=name,
            type=type,
            docstring=docstring,
            user_flags=user_flags,
            flags=flags,
            auto_var_name=auto_var_name,
            read_handler=read_handler,
            write_handler=write_handler,
        )

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.name, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.type, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.docstring, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.user_flags, IntegerCodec.IntType.UInt32, output)
        IntegerCodec.dump(self.flags, IntegerCodec.IntType.UInt8, output)

        if (self.flags & 4) != 0:
            assert self.auto_var_name is not None
            IntegerCodec.dump(self.auto_var_name, IntegerCodec.IntType.UInt16, output)

        if (self.flags & 5) == 1:
            assert self.read_handler is not None
            self.read_handler.dump(output)

        if (self.flags & 6) == 2:
            assert self.write_handler is not None
            self.write_handler.dump(output)

    @override
    def validate_model(self) -> None:
        if (self.flags & 4) != 0 and self.auto_var_name is None:
            raise ValueError("'auto_var_name' is required if `(flags & 4) != 0`!")

        if (self.flags & 5) == 1 and self.read_handler is None:
            raise ValueError("'read_handler' is required if `(flags & 5) == 1`!")

        if (self.flags & 6) == 2 and self.write_handler is None:
            raise ValueError("'write_handler' is required if `(flags & 6) == 2`!")
