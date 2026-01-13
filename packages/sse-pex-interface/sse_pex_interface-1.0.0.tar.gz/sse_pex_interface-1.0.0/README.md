# sse-pex-interface

A Python library for reading and writing compiled Papyrus Script files (.pex) for Skyrim Special Edition.

**This is neither a compiler (.psc -> .pex) nor a decompiler (.pex -> .psc)!**

## Features

- Fully symmetrical parse and dump methods
- Fully typed and documented models based on Pydantic
- Automated validation of Papyrus data

## Installation

**With pip**: `pip install sse-pex-interface`

**With uv**: `uv add sse-pex-interface`

## Basic Usage

This example demonstrates how to load a compiled Papyrus Script, modify its header and save it again:

```py
>>> from sse_pex_interface import PexFile
>>> from pathlib import Path
>>> with Path("myscript.pex").open("rb") as stream:
...     pex_file = PexFile.parse(stream)
...
>>> print(pex_file.header)
magic=4200055006 major_version=3 minor_version=2 game_id=1 compilation_time=1767530035 source_file_name='MyScript.psc' username='Cutleast' machinename='CUTLEAST-PC'
>>> pex_file.header.username = "Someone else"
>>> with Path("myscript.pex").open("wb") as stream:
...     pex_file.dump(stream)
...
>>>
```

## Credits

- [Compiled Script File Format Documentation at The Unofficial Elder Scrolls Pages](https://en.uesp.net/wiki/Skyrim_Mod:Compiled_Script_File_Format)
