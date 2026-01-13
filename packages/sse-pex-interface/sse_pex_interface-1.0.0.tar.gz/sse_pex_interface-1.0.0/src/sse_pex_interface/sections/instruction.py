"""
Copyright (c) Cutleast
"""

from enum import IntEnum
from typing import BinaryIO, Self, cast, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec
from .variable_data import VariableData


class Instruction(BinaryModel):
    """
    Model representing an instruction of a PEX file.
    """

    class OpCode(IntEnum):
        """Enum for Opcodes. See https://en.uesp.net/wiki/Skyrim_Mod:Compiled_Script_File_Format#Opcodes."""

        NOP = 0x00
        """Arguments: None; Do nothing."""

        IADD = 0x01
        """Arguments: [String, Integer, Integer]; Add two integers."""

        FADD = 0x02
        """Arguments: [String, Float, Float]; Add two floats."""

        ISUB = 0x03
        """Arguments: [String, Integer, Integer]; Subtract two integers."""

        FSUB = 0x04
        """Arguments: [String, Float, Float]; Subtract two floats."""

        IMUL = 0x05
        """Arguments: [String, Integer, Integer]; Multiply two integers."""

        FMUL = 0x06
        """Arguments: [String, Float, Float]; Multiply two floats."""

        IDIV = 0x07
        """Arguments: [String, Integer, Integer]; Divide two integers."""

        FDIV = 0x08
        """Arguments: [String, Float, Float]; Divide two floats."""

        IMOD = 0x09
        """Arguments: [String, Integer, Integer]; Remainder of two integers."""

        NOT = 0x0A
        """Arguments: [String, Any]; Flip a bool; type conversion may occur."""

        INEG = 0x0B
        """Arguments: [String, Integer]; Negate an integer."""

        FNEG = 0x0C
        """Arguments: [String, Float]; Negate a float."""

        ASSIGN = 0x0D
        """Arguments: [String, Any]; Store a variable."""

        CAST = 0x0E
        """Arguments: [String, Any]; Type conversion."""

        CMP_EQ = 0x0F
        """Arguments: [String, Any, Any]; a == b."""

        CMP_LT = 0x10
        """Arguments: [String, Any, Any]; a < b."""

        CMP_LE = 0x11
        """Arguments: [String, Any, Any]; a <= b."""

        CMP_GT = 0x12
        """Arguments: [String, Any, Any]; a > b."""

        CMP_GE = 0x13
        """Arguments: [String, Any, Any]; a >= b."""

        JMP = 0x14
        """Arguments: [Label]; Relative unconditional branch."""

        JMPT = 0x15
        """Arguments: [Any, Label]; Branch if true."""

        JMPF = 0x16
        """Arguments: [Any, Label]; Branch if false."""

        CALLMETHOD = 0x17
        """Arguments: [Identifier, String, String, *]; Call an instance method."""

        CALLPARENT = 0x18
        """Arguments: [Identifier, String, *]; Call a parent method."""

        CALLSTATIC = 0x19
        """Arguments: [Identifier, Identifier, String, *]; Call a static method."""

        RETURN = 0x1A
        """Arguments: [Any]; Return from function."""

        STRCAT = 0x1B
        """Arguments: [String, String, String]; Concatenate two strings."""

        PROPGET = 0x1C
        """Arguments: [Identifier, String, String]; Retrieve an instance property."""

        PROPSET = 0x1D
        """Arguments: [Identifier, String, Any]; Set an instance property."""

        ARRAY_CREATE = 0x1E
        """Arguments: [String, Unsigned Integer]; Create an array."""

        ARRAY_LENGTH = 0x1F
        """Arguments: [String, String]; Get array length."""

        ARRAY_GETELEMENT = 0x20
        """Arguments: [String, String, Integer]; Get array element."""

        ARRAY_SETELEMENT = 0x21
        """Arguments: [String, Integer, Any]; Set array element."""

        ARRAY_FINDELEMENT = 0x22
        """Arguments: [String, String, Integer, Integer]; Find element in array."""

        ARRAY_RFINDELEMENT = 0x23
        """Arguments: [String, String, Integer, Integer]; Reverse-find element in array."""

    op: OpCode
    """uint8: see [Opcodes](https://en.uesp.net/wiki/Skyrim_Mod:Compiled_Script_File_Format#Opcodes)"""

    arguments: list[VariableData]
    """Arguments. Length is dependen on opcode, also varargs."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        op: Instruction.OpCode = Instruction.OpCode(
            IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)
        )

        arguments: list[VariableData] = []

        fixed_arg_count: int = 0
        has_varargs: bool = False
        integer_unsigned: bool = False
        """if variable data of type integer should be interpreted as unsigned"""

        match op:
            case Instruction.OpCode.NOP:
                pass

            case (
                Instruction.OpCode.IADD
                | Instruction.OpCode.FADD
                | Instruction.OpCode.ISUB
                | Instruction.OpCode.FSUB
                | Instruction.OpCode.IMUL
                | Instruction.OpCode.FMUL
                | Instruction.OpCode.IDIV
                | Instruction.OpCode.FDIV
                | Instruction.OpCode.IMOD
                | Instruction.OpCode.CMP_EQ
                | Instruction.OpCode.CMP_LT
                | Instruction.OpCode.CMP_LE
                | Instruction.OpCode.CMP_GT
                | Instruction.OpCode.CMP_GE
                | Instruction.OpCode.STRCAT
                | Instruction.OpCode.PROPGET
                | Instruction.OpCode.PROPSET
                | Instruction.OpCode.ARRAY_GETELEMENT
                | Instruction.OpCode.ARRAY_SETELEMENT
            ):
                fixed_arg_count = 3

            case (
                Instruction.OpCode.NOT
                | Instruction.OpCode.INEG
                | Instruction.OpCode.FNEG
                | Instruction.OpCode.ASSIGN
                | Instruction.OpCode.CAST
                | Instruction.OpCode.JMPT
                | Instruction.OpCode.JMPF
            ):
                fixed_arg_count = 2

            case Instruction.OpCode.JMP | Instruction.OpCode.RETURN:
                fixed_arg_count = 1

            case Instruction.OpCode.CALLMETHOD | Instruction.OpCode.CALLSTATIC:
                fixed_arg_count = 3
                has_varargs = True

            case Instruction.OpCode.CALLPARENT:
                fixed_arg_count = 2
                has_varargs = True

            case Instruction.OpCode.ARRAY_CREATE | Instruction.OpCode.ARRAY_LENGTH:
                fixed_arg_count = 2

                if op == Instruction.OpCode.ARRAY_CREATE:
                    integer_unsigned = True

            case (
                Instruction.OpCode.ARRAY_FINDELEMENT
                | Instruction.OpCode.ARRAY_RFINDELEMENT
            ):
                fixed_arg_count = 4

        for _ in range(fixed_arg_count):
            arguments.append(VariableData.parse(stream, integer_unsigned))

        if has_varargs:
            vararg_count: VariableData = VariableData.parse(stream)
            arguments.append(vararg_count)

            count: int = cast(int, vararg_count.data)
            for _ in range(count):
                arguments.append(VariableData.parse(stream, integer_unsigned))

        return cls(op=op, arguments=arguments)

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.op, IntegerCodec.IntType.UInt8, output)

        for argument in self.arguments:
            argument.dump(output)
