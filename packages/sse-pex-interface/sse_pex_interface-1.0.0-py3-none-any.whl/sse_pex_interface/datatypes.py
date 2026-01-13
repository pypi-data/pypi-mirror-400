"""
Copyright (c) Cutleast
"""

import struct
from enum import Enum, IntFlag, auto
from typing import BinaryIO, Literal, Optional, Self, overload


class IntegerCodec:
    """
    Codec class for all types of signed and unsigned integers.
    """

    class IntType(Enum):
        UInt8 = (1, False)
        """Unsigned integer of size 1."""

        UInt16 = (2, False)
        """Unsigned integer of size 2."""

        UInt32 = (4, False)
        """Unsigned integer of size 4."""

        UInt64 = (8, False)
        """Unsigned integer of size 8."""

        UShort = (2, False)
        """Same as UInt16."""

        ULong = (4, False)
        """Same as UInt32."""

        Int8 = (1, True)
        """Signed integer of size 1."""

        Int16 = (2, True)
        """Signed integer of size 2."""

        Int32 = (4, True)
        """Signed integer of size 4."""

        Int64 = (8, True)
        """Signed integer of size 8."""

        Short = (2, True)
        """Same as Int16."""

        Long = (4, True)
        """Same as Int32."""

    @staticmethod
    def parse(stream: BinaryIO, type: IntType) -> int:
        """
        Parses an integer of the specified type from a byte stream.

        Args:
            stream (BinaryIO): Byte stream to read from.
            type (IntType): Integer type.

        Returns:
            int: Parsed integer.
        """

        size: int
        signed: bool
        size, signed = type.value

        return int.from_bytes(stream.read(size), byteorder="big", signed=signed)

    @staticmethod
    def dump(value: int, type: IntType, output: BinaryIO) -> None:
        """
        Dumps an integer of the specified type to a byte stream.

        Args:
            value (int): Integer.
            type (IntType): Integer type.
            output (BinaryIO): Byte stream to write to.
        """

        size: int
        signed: bool
        size, signed = type.value

        output.write(value.to_bytes(size, byteorder="big", signed=signed))


class StringCodec:
    """
    Codec class for all types of chars and strings.
    """

    ENCODING: str = "cp1252"
    """The default encoding used in Bethesda's file formats."""

    class StrType(Enum):
        Char = auto()
        """8-bit character."""

        WChar = auto()
        """16-bit character."""

        String = auto()
        """Not-terminated string."""

        WString = auto()
        """Not-terminated string prefixed by UInt16."""

        BZString = auto()
        """Null-terminated string prefixed by UInt8."""

        BString = auto()
        """Not-terminated string prefixed by UInt8."""

        List = auto()
        """List of strings separated by `\\x00`."""

    @staticmethod
    @overload
    def parse(
        stream: BinaryIO, type: Literal[StrType.Char], size: Literal[1] = 1
    ) -> str: ...

    @staticmethod
    @overload
    def parse(
        stream: BinaryIO, type: Literal[StrType.WChar], size: Literal[1] = 1
    ) -> str: ...

    @staticmethod
    @overload
    def parse(stream: BinaryIO, type: Literal[StrType.String], size: int) -> str: ...

    @staticmethod
    @overload
    def parse(
        stream: BinaryIO, type: Literal[StrType.WString], size: None = None
    ) -> str: ...

    @staticmethod
    @overload
    def parse(
        stream: BinaryIO, type: Literal[StrType.BString], size: None = None
    ) -> str: ...

    @staticmethod
    @overload
    def parse(
        stream: BinaryIO, type: Literal[StrType.BZString], size: None = None
    ) -> str: ...

    @staticmethod
    @overload
    def parse(
        stream: BinaryIO, type: Literal[StrType.List], size: int
    ) -> list[str]: ...

    @staticmethod
    def parse(
        stream: BinaryIO, type: StrType, size: Optional[int] = None
    ) -> list[str] | str:
        """
        Parses a string of the specified type from a byte stream.

        Args:
            stream (BinaryIO): Byte stream to read from.
            type (StrType): String type.
            size (Optional[int], optional): Size of the string(s). Defaults to None.

        Returns:
            list[str] | str: Parsed string(s).
        """

        match type:
            case StringCodec.StrType.Char:
                text = stream.read(1)

            case StringCodec.StrType.WChar:
                text = stream.read(2)

            case StringCodec.StrType.String:
                if size is None:
                    raise ValueError("'size' must not be None when 'type' is 'String'!")

                text = stream.read(size)

            case StringCodec.StrType.WString:
                size = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
                text = stream.read(size)

            case StringCodec.StrType.BZString | type.BString:
                size = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)
                text = stream.read(size).strip(b"\x00")

            case StringCodec.StrType.List:
                strings: list[str] = []

                if size is None:
                    raise ValueError("'size' must not be None when 'type' is 'List'!")

                while len(strings) < size:
                    string = b""
                    while (char := stream.read(1)) != b"\x00" and char:
                        string += char

                    if string:
                        strings.append(string.decode(StringCodec.ENCODING))

                return strings

        return text.decode(StringCodec.ENCODING)

    @staticmethod
    @overload
    def dump(
        value: list[str], type: Literal[StrType.List], output: BinaryIO
    ) -> None: ...

    @staticmethod
    @overload
    def dump(
        value: str,
        type: Literal[
            StrType.Char,
            StrType.WChar,
            StrType.String,
            StrType.WString,
            StrType.BString,
            StrType.BZString,
        ],
        output: BinaryIO,
    ) -> None: ...

    @staticmethod
    def dump(value: list[str] | str, type: StrType, output: BinaryIO) -> None:
        """
        Dumps a string of the specified type to a byte stream.

        Args:
            value (list[str] | str): String or list of strings to dump.
            type (StrType): String type.
            output (BinaryIO): Byte stream to write to.
        """

        match type:
            case (
                StringCodec.StrType.Char
                | StringCodec.StrType.WChar
                | StringCodec.StrType.String
            ):
                if not isinstance(value, str):
                    raise TypeError("'value' must be a string!")

                output.write(value.encode(StringCodec.ENCODING))

            case StringCodec.StrType.WString:
                if not isinstance(value, str):
                    raise TypeError("'value' must be a string!")

                text = value.encode(StringCodec.ENCODING)
                IntegerCodec.dump(len(text), IntegerCodec.IntType.UInt16, output)
                output.write(text)

            case StringCodec.StrType.BString:
                if not isinstance(value, str):
                    raise TypeError("'value' must be a string!")

                text = value.encode(StringCodec.ENCODING)
                IntegerCodec.dump(len(text), IntegerCodec.IntType.UInt8, output)
                output.write(text)

            case StringCodec.StrType.BZString:
                if not isinstance(value, str):
                    raise TypeError("'value' must be a string!")

                text = value.encode(StringCodec.ENCODING) + b"\x00"
                IntegerCodec.dump(len(text), IntegerCodec.IntType.UInt8, output)
                output.write(text)

            case StringCodec.StrType.List:
                if not isinstance(value, list):
                    raise TypeError("'value' must be a list!")

                for string in value:
                    output.write(string.encode(StringCodec.ENCODING) + b"\x00")


class FloatCodec:
    """
    Codec class for all types of floats.
    """

    class FloatType(Enum):
        """
        Various float types used by Bethesda in their game files.
        """

        Float32 = (4, "f")
        """Float of Size 4."""

        Float64 = (8, "d")
        """Float of Size 8."""

        Float = (4, "f")
        """Alias for Float32."""

        Double = (8, "d")
        """Alias for Float64."""

    @staticmethod
    def parse(stream: BinaryIO, type: FloatType) -> float:
        """
        Parses a float from a byte stream.

        Args:
            stream (BinaryIO): Byte stream to read from.
            type (FloatType): Float type.

        Returns:
            float: Parsed Python float.
        """

        size, format = type.value

        value: float = struct.unpack(format, stream.read(size))[0]
        return value

    @staticmethod
    def dump(value: float, type: FloatType, output: BinaryIO) -> None:
        """
        Dumps a float to a byte stream.

        Args:
            value (float): Float to dump.
            type (FloatType): Float type.
            output (BinaryIO): Byte stream to write to.
        """

        size, format = type.value  # type: ignore
        output.write(struct.pack(format, value))


class Flags(IntFlag):
    """
    Class for all types of flags.
    """

    @classmethod
    def parse(cls, stream: BinaryIO, type: IntegerCodec.IntType) -> Self:
        """
        Parses a flag from a byte stream.

        Args:
            stream (BinaryIO): Byte stream to read from.
            type (Integer.IntType): Integer type.

        Returns:
            Self: Parsed flag.
        """

        value: int = IntegerCodec.parse(stream, type)
        flag = cls(value)

        return flag

    def dump(self, type: IntegerCodec.IntType, output: BinaryIO) -> None:
        """
        Dumps a flag to a byte stream.

        Args:
            type (Integer.IntType): Integer type.
            output (BinaryIO): Byte stream to write to.
        """

        IntegerCodec.dump(self.value, type, output)
