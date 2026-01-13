"""
Base Node class for all TypeScript AST nodes.

This module implements the core abstraction for AST nodes following
the Composite pattern - nodes can contain other nodes.
"""

from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar, Sequence, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from pytsast.core.types import Undefined

if TYPE_CHECKING:
    from pytsast.core.types import SerializedFactory, SerializedNode


class Node(BaseModel, ABC):
    """
    Abstract base class for all TypeScript AST nodes.

    Each subclass must define:
    - factory_name: The TypeScript factory method name
    (e.g., "createIdentifier")

    The args are automatically derived from the model fields in order.

    Example:
        class Identifier(Node):
            factory_name = "createIdentifier"
            text: str

        id = Identifier(text="myVar")
        id.serialize()  # {"type": "factory", "name": "createIdentifier",
          "args": [...]}
    """

    factory_name: ClassVar[str]

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    def _get_ordered_args(self) -> tuple[Any, ...]:
        """
        Get the node's arguments in field definition order.

        Override this method if you need custom argument ordering.
        """
        return tuple(getattr(self, field) for field in self.model_fields)

    def serialize(self) -> "SerializedFactory":
        """
        Serialize this node to a factory call representation.

        Returns a SerializedFactory that can be converted to JSON and
        processed by the TypeScript parser.
        """
        from pytsast.core.serializer import Serializer

        return Serializer.serialize_node(self)

    def __repr__(self) -> str:
        args = ", ".join(repr(v) for v in self._get_ordered_args())
        return f"{self.__class__.__name__}({args})"


class NodeList(BaseModel):
    """
    Represents a list of nodes (e.g., array of statements).

    This is a wrapper that serializes to a JSON array.
    """

    items: Sequence[Node | Undefined]

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    def serialize(self) -> list["SerializedNode"]:
        """Serialize all items in the list."""
        from pytsast.core.serializer import Serializer

        return [Serializer.serialize_value(item) for item in self.items]

    def __repr__(self) -> str:
        return f"NodeList({self.items!r})"

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)
