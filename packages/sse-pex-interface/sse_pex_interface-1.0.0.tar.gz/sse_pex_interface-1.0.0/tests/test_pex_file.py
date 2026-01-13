"""
Copyright (c) Cutleast
"""

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from sse_pex_interface.pex_file import PexFile


class TestPexFile:
    """
    Tests reading and writing an entire PEX file.
    """

    def test_parse(self) -> None:
        """
        Tests parsing a PEX file.
        """

        # given
        pex_file_path: Path = Path.cwd() / "tests" / "test_data" / "_wetquestscript.pex"

        # when
        with pex_file_path.open("rb") as stream:
            pex_file: PexFile = PexFile.parse(stream)

        # then
        assert pex_file.header.compilation_time == 1601329996
        assert pex_file.header.source_file_name == "_WetQuestScript.psc"
        assert pex_file.header.username == "TechAngel"
        assert pex_file.header.machinename == "DESKTOP-O95F7AQ"
        assert len(pex_file.string_table) == 624
        assert pex_file.string_table[:5] == [
            "_wetquestscript",
            "",
            "GetState",
            "GotoState",
            "ScanArea",
        ]
        assert pex_file.debug_info.has_debug_info == 1
        assert pex_file.debug_info.functions is not None
        assert len(pex_file.debug_info.functions) == 14
        assert len(pex_file.user_flags) == 2

    def test_dump(self) -> None:
        """
        Tests writing an entire PEX file.
        """

        # given
        pex_file_path: Path = Path.cwd() / "tests" / "test_data" / "_wetquestscript.pex"
        output: BinaryIO = BytesIO()
        with pex_file_path.open("rb") as stream:
            pex_file: PexFile = PexFile.parse(stream)

        # when
        pex_file.dump(output)
        output.seek(0)
        dumped_pex_file: PexFile = PexFile.parse(output)

        # then
        assert pex_file == dumped_pex_file

        # when (verify that the parser is symmetrical)
        original_data: bytes = pex_file_path.read_bytes()
        output.seek(0)
        dumped_data: bytes = output.read()

        # then
        assert dumped_data == original_data
