"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Literal, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec, StringCodec


class Header(BinaryModel):
    """
    Model that represents the header of a PEX file.
    """

    magic: Literal[0xFA57C0DE]
    """uint32: Must be 0xFA57C0DE."""

    major_version: Literal[3]
    """uint8: The major version of the Papyrus Script. Only 3 is supported."""

    minor_version: Literal[1, 2]
    """uint8: The minor version of the Papyrus Script. Only 1 and 2 are supported."""

    game_id: Literal[1]
    """uint16: The game ID of the Papyrus Script. Only 1 (Skyrim) is supported."""

    compilation_time: int
    """uint64: The compilation timestamp (seconds since epoch)."""

    source_file_name: str
    """wstring: Name of the source file this file was compiled from."""

    username: str
    """wstring: Username used to compile the script."""

    machinename: str
    """wstring: Machine name used to compile the script."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        magic: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt32)
        major_version: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)
        minor_version: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt8)
        game_id: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        compilation_time: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt64)
        source_file_name: str = StringCodec.parse(stream, StringCodec.StrType.WString)
        username: str = StringCodec.parse(stream, StringCodec.StrType.WString)
        machinename: str = StringCodec.parse(stream, StringCodec.StrType.WString)

        assert magic == 0xFA57C0DE, "File format not supported!"
        assert major_version == 3, "File format not supported!"
        assert minor_version == 1 or minor_version == 2, "File format not supported!"
        assert game_id == 1, "File format not supported!"

        return cls(
            magic=magic,
            major_version=major_version,
            minor_version=minor_version,
            game_id=game_id,
            compilation_time=compilation_time,
            source_file_name=source_file_name,
            username=username,
            machinename=machinename,
        )

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.magic, IntegerCodec.IntType.UInt32, output)
        IntegerCodec.dump(self.major_version, IntegerCodec.IntType.UInt8, output)
        IntegerCodec.dump(self.minor_version, IntegerCodec.IntType.UInt8, output)
        IntegerCodec.dump(self.game_id, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.compilation_time, IntegerCodec.IntType.UInt64, output)
        StringCodec.dump(self.source_file_name, StringCodec.StrType.WString, output)
        StringCodec.dump(self.username, StringCodec.StrType.WString, output)
        StringCodec.dump(self.machinename, StringCodec.StrType.WString, output)
