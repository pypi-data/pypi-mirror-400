"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Optional, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec
from .debug_function import DebugFunction


class DebugInfo(BinaryModel):
    """
    Model representing the debug info of a PEX file.
    """

    has_debug_info: int
    """uint8: If zero then no debug info is present."""

    modification_time: Optional[int]
    """
    uint64: Modification time of the file. Only present if `has_debug_info` is non-zero.
    """

    functions: Optional[list[DebugFunction]]
    """list: List of functions. Only present if `has_debug_info` is non-zero."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        has_debug_info: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)

        modification_time: Optional[int] = None
        functions: Optional[list[DebugFunction]] = None

        if has_debug_info != 0:
            modification_time = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt64)

            function_count: int = IntegerCodec.parse(
                stream, IntegerCodec.IntType.UInt16
            )
            functions = []
            for _ in range(function_count):
                functions.append(DebugFunction.parse(stream))

        return cls(
            has_debug_info=has_debug_info,
            modification_time=modification_time,
            functions=functions,
        )

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.has_debug_info, IntegerCodec.IntType.UInt8, output)

        if self.has_debug_info != 0:
            assert self.modification_time is not None
            IntegerCodec.dump(
                self.modification_time, IntegerCodec.IntType.UInt64, output
            )

            assert self.functions is not None
            IntegerCodec.dump(len(self.functions), IntegerCodec.IntType.UInt16, output)
            for function in self.functions:
                function.dump(output)

    @override
    def validate_model(self) -> None:
        if self.has_debug_info != 0:
            if self.modification_time is None:
                raise ValueError(
                    "Modification time is required when has_debug_info is non-zero."
                )

            if self.functions is None:
                raise ValueError(
                    "Functions are required when has_debug_info is non-zero."
                )
