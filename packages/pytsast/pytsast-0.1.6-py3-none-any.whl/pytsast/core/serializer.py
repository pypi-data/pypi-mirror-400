"""
Serializer for converting Python AST nodes to JSON-serializable format.

This module implements the Visitor pattern for serializing different
types of values to their appropriate JSON representation.
"""

from typing import TYPE_CHECKING, Any

from pytsast.core.types import (
    Undefined,
    SerializedFactory,
    SerializedLiteral,
    SerializedUndefined,
    SerializedNumber,
    SerializedNode,
)

if TYPE_CHECKING:
    from pytsast.core.base import Node


class Serializer:
    """
    Serializes Python AST nodes to JSON-serializable dictionaries.

    This class uses a strategy pattern to handle different value types:
    - Undefined -> SerializedUndefined
    - None, bool, str -> SerializedLiteral
    - int, float -> SerializedNumber
    - Node -> SerializedFactory (recursive)
    - Sequence -> list of serialized values
    """

    @classmethod
    def serialize_value(cls, value: Any) -> SerializedNode:
        """
        Serialize any value to its appropriate JSON representation.

        Args:
            value: The value to serialize (Node, literal, or sequence)

        Returns:
            A SerializedNode (Literal, Number, or Factory)

        Raises:
            TypeError: If the value type is not supported
        """
        # Handle Undefined
        if Undefined.is_undefined(value):
            return SerializedUndefined()

        # Handle None, bool, str -> Literal
        if value is None or isinstance(value, (bool, str)):
            return SerializedLiteral(value=value)

        # Handle numbers -> Number
        if isinstance(value, int):
            return SerializedNumber(value=value)

        if isinstance(value, float):
            # Floats are serialized as strings to preserve precision
            return SerializedNumber(value=str(value))

        # Handle Node -> recursive serialization
        from pytsast.core.base import Node, NodeList

        if isinstance(value, Node):
            return cls.serialize_node(value)

        # Handle NodeList -> array
        if isinstance(value, NodeList):
            return SerializedFactory(
                name="__array__",
                args=value.serialize(),
            )

        # Handle sequences (list, tuple) -> array
        if isinstance(value, (list, tuple)):
            return SerializedFactory(
                name="__array__",
                args=[cls.serialize_value(item) for item in value],
            )

        raise TypeError(
            f"Cannot serialize value of type {type(value).__name__}: {value!r}"
        )

    @classmethod
    def serialize_node(cls, node: "Node") -> SerializedFactory:
        """
        Serialize a Node to a SerializedFactory.

        Args:
            node: The AST node to serialize

        Returns:
            A SerializedFactory representing the node
        """
        args = node._get_ordered_args()
        serialized_args = [cls.serialize_value(arg) for arg in args]

        return SerializedFactory(
            name=node.factory_name,
            args=serialized_args,
        )

    @classmethod
    def to_dict(cls, node: "Node") -> dict:
        """
        Serialize a node to a plain Python dictionary.

        Useful for JSON serialization with json.dumps().
        """
        return cls.serialize_node(node).model_dump()

    @classmethod
    def to_json(cls, node: "Node", **kwargs) -> str:
        """
        Serialize a node directly to a JSON string.

        Args:
            node: The AST node to serialize
            **kwargs: Additional arguments passed to model_dump_json()

        Returns:
            JSON string representation
        """
        return cls.serialize_node(node).model_dump_json(**kwargs)
