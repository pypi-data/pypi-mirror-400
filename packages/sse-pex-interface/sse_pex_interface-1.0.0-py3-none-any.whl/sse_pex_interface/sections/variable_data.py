"""
Copyright (c) Cutleast
"""

from enum import IntEnum
from typing import BinaryIO, Optional, Self, override

from ..binary_model import BinaryModel
from ..datatypes import FloatCodec, IntegerCodec


class VariableData(BinaryModel):
    """
    Model representing the data of a variable.
    """

    class Type(IntEnum):
        """Enum for the variable types."""

        NULL = 0
        IDENTIFIER = 1
        STRING = 2
        INTEGER = 3
        FLOAT = 4
        BOOL = 5

    type: Type
    """uint8: Type of the variable."""

    data: Optional[int | float]
    """uint16 | int32 | uint32 | float32 | uint8: Data of the variable."""

    integer_unsigned: bool
    """If the variable type is integer, the data is interpreted as an uint32."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO, integer_unsigned: bool = False) -> Self:
        type = cls.Type(IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8))

        data: Optional[int | float] = None
        match type:
            case VariableData.Type.NULL:
                pass
            case VariableData.Type.IDENTIFIER | VariableData.Type.STRING:
                data = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
            case VariableData.Type.INTEGER:
                if integer_unsigned:
                    data = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt32)
                else:
                    data = IntegerCodec.parse(stream, IntegerCodec.IntType.Int32)
            case VariableData.Type.FLOAT:
                data = FloatCodec.parse(stream, FloatCodec.FloatType.Float32)
            case VariableData.Type.BOOL:
                data = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)

        return cls(type=type, data=data, integer_unsigned=integer_unsigned)

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.type, IntegerCodec.IntType.UInt8, output)

        match self.type:
            case VariableData.Type.NULL:
                pass

            case VariableData.Type.IDENTIFIER | VariableData.Type.STRING:
                assert isinstance(self.data, int)
                IntegerCodec.dump(self.data, IntegerCodec.IntType.UInt16, output)

            case VariableData.Type.INTEGER:
                assert isinstance(self.data, int)

                if self.integer_unsigned:
                    IntegerCodec.dump(self.data, IntegerCodec.IntType.UInt32, output)
                else:
                    IntegerCodec.dump(self.data, IntegerCodec.IntType.Int32, output)

            case VariableData.Type.FLOAT:
                assert isinstance(self.data, float)
                FloatCodec.dump(self.data, FloatCodec.FloatType.Float32, output)

            case VariableData.Type.BOOL:
                assert isinstance(self.data, int)
                IntegerCodec.dump(self.data, IntegerCodec.IntType.UInt8, output)

    @override
    def validate_model(self) -> None:
        match self.type:
            case VariableData.Type.NULL:
                if self.data is not None:
                    raise TypeError("Data for type 'NULL' must be None!")

            case (
                VariableData.Type.IDENTIFIER
                | VariableData.Type.STRING
                | VariableData.Type.INTEGER
                | VariableData.Type.BOOL
            ):
                if not isinstance(self.data, int):
                    raise TypeError(f"Data for type '{self.type}' must be an integer!")

            case VariableData.Type.FLOAT:
                if not isinstance(self.data, float):
                    raise TypeError(f"Data for type '{self.type}' must be a float!")
