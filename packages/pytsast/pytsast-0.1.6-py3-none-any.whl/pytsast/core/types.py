"""
Serialization types for JSON output.

These types define the structure of the serialized AST that will be
consumed by the TypeScript parser.
"""

from typing import Literal, TypeIs, Union
from pydantic import BaseModel


class SerializedLiteral(BaseModel):
    """Represents a literal value (null, bool, string)."""

    type: Literal["literal"] = "literal"
    value: None | bool | str

    model_config = {"frozen": True}


class SerializedNumber(BaseModel):
    """Represents a numeric value (int or float as string)."""

    type: Literal["number"] = "number"
    value: int | str  # int for integers, str for floats

    model_config = {"frozen": True}


class SerializedUndefined(BaseModel):
    """Represents an undefined value."""

    type: Literal["undefined"] = "undefined"

    model_config = {"frozen": True}


class SerializedFactory(BaseModel):
    """Represents a factory function call."""

    type: Literal["factory"] = "factory"
    name: str
    args: list["SerializedNode"]

    model_config = {"frozen": True}


class Undefined:

    @staticmethod
    def __bool__():
        return False

    @staticmethod
    def is_undefined(value) -> TypeIs["Undefined"]:
        if value is Undefined or isinstance(value, Undefined):
            return True
        return False


undefined = Undefined()

# Union of all serialized node types
SerializedNode = Union[
    SerializedLiteral,
    SerializedNumber,
    SerializedFactory,
    SerializedUndefined,
]

# Type alias for literal Python values that can be serialized
LiteralValue = None | bool | str | int | float


__all__ = [
    "SerializedLiteral",
    "SerializedNumber",
    "SerializedUndefined",
    "SerializedFactory",
    "SerializedNode",
    "LiteralValue",
    "Undefined",
    "undefined",
]
