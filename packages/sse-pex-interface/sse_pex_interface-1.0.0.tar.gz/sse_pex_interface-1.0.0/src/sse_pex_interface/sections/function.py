"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec
from .instruction import Instruction
from .variable_type import VariableType


class Function(BinaryModel):
    """
    Model for a function of a PEX file.
    """

    return_type: int
    """uint16: Index(base 0) into string table."""

    docstring: int
    """uint16: Index(base 0) into string table."""

    user_flags: int
    """uint32: User flags."""

    flags: int
    """
    uint8: Function flags:
    
    - bit 0 = global function
    - bit 1 = native function (i.e., no code)
    """

    params: list[VariableType]
    """List of parameter types."""

    locals: list[VariableType]
    """List of local variable types."""

    instructions: list[Instruction]
    """List of instructions."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        return_type: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        docstring: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        user_flags: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt32)
        flags: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)

        num_params: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        params: list[VariableType] = []
        for _ in range(num_params):
            params.append(VariableType.parse(stream))

        num_locals: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        locals: list[VariableType] = []
        for _ in range(num_locals):
            locals.append(VariableType.parse(stream))

        num_instructions: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        instructions: list[Instruction] = []
        for _ in range(num_instructions):
            instructions.append(Instruction.parse(stream))

        return cls(
            return_type=return_type,
            docstring=docstring,
            user_flags=user_flags,
            flags=flags,
            params=params,
            locals=locals,
            instructions=instructions,
        )

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.return_type, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.docstring, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.user_flags, IntegerCodec.IntType.UInt32, output)
        IntegerCodec.dump(self.flags, IntegerCodec.IntType.UInt8, output)

        IntegerCodec.dump(len(self.params), IntegerCodec.IntType.UInt16, output)
        for param in self.params:
            param.dump(output)

        IntegerCodec.dump(len(self.locals), IntegerCodec.IntType.UInt16, output)
        for local in self.locals:
            local.dump(output)

        IntegerCodec.dump(len(self.instructions), IntegerCodec.IntType.UInt16, output)
        for instruction in self.instructions:
            instruction.dump(output)
