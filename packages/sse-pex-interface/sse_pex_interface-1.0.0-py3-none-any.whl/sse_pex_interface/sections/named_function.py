"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec
from .function import Function


class NamedFunction(BinaryModel):
    """
    Model for a named function of a PEX file.
    """

    function_name: int
    """uint16: Index(base 0) into string table."""

    function: Function
    """The actual function."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        function_name: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        function: Function = Function.parse(stream)

        return cls(function_name=function_name, function=function)

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.function_name, IntegerCodec.IntType.UInt16, output)

        self.function.dump(output)
