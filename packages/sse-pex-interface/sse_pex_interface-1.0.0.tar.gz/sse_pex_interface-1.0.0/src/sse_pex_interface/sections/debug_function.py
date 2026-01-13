"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Literal, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec


class DebugFunction(BinaryModel):
    """
    Model representing a debug function of a PEX file.
    """

    object_name_index: int
    """uint16: Index(base 0) into string table."""

    state_name_index: int
    """uint16: Index(base 0) into string table."""

    function_name_index: int
    """uint16: Index(base 0) into string table."""

    function_type: Literal[0, 1, 2, 3]
    """uint8: Function type."""

    line_numbers: list[int]
    """uint16[instruction_count]: Maps instructions to their original lines in the source."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        object_name_index: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        state_name_index: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        function_name_index: int = IntegerCodec.parse(
            stream, IntegerCodec.IntType.UInt16
        )
        function_type: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)

        instruction_count: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        line_numbers: list[int] = []
        for _ in range(instruction_count):
            line_numbers.append(IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16))

        assert (
            function_type == 0
            or function_type == 1
            or function_type == 2
            or function_type == 3
        ), f"Function type {function_type} not supported!"

        return cls(
            object_name_index=object_name_index,
            state_name_index=state_name_index,
            function_name_index=function_name_index,
            function_type=function_type,
            line_numbers=line_numbers,
        )

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.object_name_index, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.state_name_index, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.function_name_index, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.function_type, IntegerCodec.IntType.UInt8, output)

        IntegerCodec.dump(len(self.line_numbers), IntegerCodec.IntType.UInt16, output)
        for line_number in self.line_numbers:
            IntegerCodec.dump(line_number, IntegerCodec.IntType.UInt16, output)
