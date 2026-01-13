"""
Helper functions to call tsparser CLI from Python.

Usage:
    from pytsast.cli import generate_typescript

    import pytsast.factory as ts

    nodes = [
        ts.createImportDeclaration(
            None,
            ts.createImportClause(
                False,
                ts.createIdentifier("zod"),
                None,
            ),
            ts.createStringLiteral("zod"),
            None,
        )
    ]

    generate_typescript(nodes, "output.ts")
"""

import json
import subprocess
from pathlib import Path
from typing import Sequence

from pytsast.core.base import Node


def serialize_nodes(nodes: Sequence[Node]) -> str:
    """
    Serialize a list of AST nodes to JSON.

    Args:
        nodes: List of AST nodes to serialize

    Returns:
        JSON string representation
    """
    serialized = [node.serialize().model_dump() for node in nodes]
    return json.dumps(serialized)


def generate_typescript(
    nodes: Sequence[Node],
    output_path: str | Path,
    tsparser_path: str | Path | None = None,
    header: str | None = None,
) -> None:
    """
    Generate a TypeScript file from AST nodes.

    Args:
        nodes: List of AST nodes to generate
        output_path: Path to the output .ts file
        tsparser_path: Path to tsparser CLI (optional, uses npx
            by default)
        header: Optional header comment to prepend to the file

    Raises:
        subprocess.CalledProcessError: If tsparser fails
        FileNotFoundError: If tsparser is not found
    """
    output_path = Path(output_path)

    # Serialize nodes to JSON
    json_input = serialize_nodes(nodes)

    # Build command
    if tsparser_path:
        cmd = ["node", str(tsparser_path), "-o", str(output_path)]
    else:
        cmd = ["npx", "tsparser", "-o", str(output_path)]

    # Run tsparser with JSON input via stdin
    result = subprocess.run(
        cmd,
        input=json_input,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"tsparser failed with code {result.returncode}:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    # If header provided, prepend it to the file
    if header:
        content = output_path.read_text(encoding="utf-8")
        output_path.write_text(header + content, encoding="utf-8")


def generate_typescript_inline(
    nodes: Sequence[Node],
    tsparser_path: str | Path | None = None,
) -> str:
    """
    Generate TypeScript code as a string (without writing to file).

    Args:
        nodes: List of AST nodes to generate
        tsparser_path: Path to tsparser CLI (optional)

    Returns:
        Generated TypeScript code as string

    Note:
        This creates a temporary file and reads it back.
        For performance-critical code, consider using the
        TypeScript library directly.
    """
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".ts",
        delete=False,
        mode="r",
    ) as f:
        temp_path = Path(f.name)

    try:
        generate_typescript(nodes, temp_path, tsparser_path)
        return temp_path.read_text(encoding="utf-8")
    finally:
        temp_path.unlink(missing_ok=True)
