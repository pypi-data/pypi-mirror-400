"""
Copyright (c) Cutleast
"""

from typing import BinaryIO, Self, override

from ..binary_model import BinaryModel
from ..datatypes import IntegerCodec
from .property import Property
from .state import State
from .variable import Variable


class ObjectData(BinaryModel):
    """
    Model for the data of an object of a PEX file.
    """

    parent_class_name: int
    """uint16: Index(base 0) into string table."""

    docstring: int
    """uint16: Index(base 0) into string table."""

    user_flags: int
    """uint32: User flags."""

    auto_state_name: int
    """uint16: Index(base 0) into string table."""

    variables: list[Variable]
    """List of variables."""

    properties: list[Property]
    """List of properties."""

    states: list[State]
    """List of states."""

    @override
    @classmethod
    def parse(cls, stream: BinaryIO) -> Self:
        parent_class_name: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        docstring: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        user_flags: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt32)
        auto_state_name: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)

        num_variables: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        variables: list[Variable] = []
        for _ in range(num_variables):
            variables.append(Variable.parse(stream))

        num_properties: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        properties: list[Property] = []
        for _ in range(num_properties):
            properties.append(Property.parse(stream))

        num_states: int = IntegerCodec.parse(stream, IntegerCodec.IntType.UInt16)
        states: list[State] = []
        for _ in range(num_states):
            states.append(State.parse(stream))

        return cls(
            parent_class_name=parent_class_name,
            docstring=docstring,
            user_flags=user_flags,
            auto_state_name=auto_state_name,
            variables=variables,
            properties=properties,
            states=states,
        )

    @override
    def dump(self, output: BinaryIO) -> None:
        IntegerCodec.dump(self.parent_class_name, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.docstring, IntegerCodec.IntType.UInt16, output)
        IntegerCodec.dump(self.user_flags, IntegerCodec.IntType.UInt32, output)
        IntegerCodec.dump(self.auto_state_name, IntegerCodec.IntType.UInt16, output)

        IntegerCodec.dump(len(self.variables), IntegerCodec.IntType.UInt16, output)
        for variable in self.variables:
            variable.dump(output)

        IntegerCodec.dump(len(self.properties), IntegerCodec.IntType.UInt16, output)
        for property in self.properties:
            property.dump(output)

        IntegerCodec.dump(len(self.states), IntegerCodec.IntType.UInt16, output)
        for state in self.states:
            state.dump(output)
