"""
Copyright (c) Cutleast
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Self

from pydantic import BaseModel, ConfigDict, model_validator


class BinaryModel(BaseModel, ABC):
    """
    Abstract base class for all models that can be deserialized from and serialized to
    binary.
    """

    model_config = ConfigDict(validate_assignment=True)

    @classmethod
    @abstractmethod
    def parse(cls, stream: BinaryIO) -> Self:
        """
        Parses the model from a stream of bytes.

        Args:
            stream (BinaryIO): Byte stream to read from.

        Returns:
            Self: The parsed model.
        """

    @abstractmethod
    def dump(self, output: BinaryIO) -> None:
        """
        Writes the model's data to a stream of bytes.

        Args:
            output (BinaryIO): Byte stream to write to.
        """

    def validate_model(self) -> None:
        """
        Validates the model's data after deserialization from bytes.

        Raises:
            ValidationError: If the model's data is invalid.
        """

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        self.validate_model()

        return self
