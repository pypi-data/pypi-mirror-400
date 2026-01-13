"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Self, override

from .binary_model import BinaryModel
from .datatypes import IntegerCodec, StringCodec
from .sections import DebugInfo, Header, Object, UserFlag


class PexFile(BinaryModel):
    """
    Model for the entire PEX file.
    """

    header: Header
    """The header of the PEX file."""

    string_table: list[str]
    """The string table of the PEX file."""

    debug_info: DebugInfo
    """The debug info of the PEX file."""

    user_flags: list[UserFlag]
    """The user flags of the PEX file."""

    objects: list[Object]
    """The objects of the PEX file."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        header: Header = Header.parse(stream)

        string_count: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        string_table: list[str] = []
        for _ in range(string_count):
            string_table.append(StringCodec.parse(stream, StringCodec.StrType.WString))

        debug_info: DebugInfo = DebugInfo.parse(stream)

        user_flag_count: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        user_flags: list[UserFlag] = []
        for _ in range(user_flag_count):
            user_flags.append(UserFlag.parse(stream))

        object_count: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        objects: list[Object] = []
        for _ in range(object_count):
            objects.append(Object.parse(stream))

        return cls(
            header=header,
            string_table=string_table,
            debug_info=debug_info,
            user_flags=user_flags,
            objects=objects,
        )

    @override
    def dump(self, output: BinaryIO) -> None:
        self.header.dump(output)

        IntegerCodec.dump(len(self.string_table), IntegerCodec.IntType.UInt16, output)
        for string in self.string_table:
            StringCodec.dump(string, StringCodec.StrType.WString, output)

        self.debug_info.dump(output)

        IntegerCodec.dump(len(self.user_flags), IntegerCodec.IntType.UInt16, output)
        for user_flag in self.user_flags:
            user_flag.dump(output)

        IntegerCodec.dump(len(self.objects), IntegerCodec.IntType.UInt16, output)
        for object in self.objects:
            object.dump(output)
