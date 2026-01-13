# pytsast - Python TypeScript AST Generator

Generate TypeScript code from Python using TypeScript's AST factory API.

This library provides a Python interface to TypeScript's AST factory functions, allowing you to build TypeScript AST nodes programmatically and serialize them to JSON for consumption by TypeScript parsers like `@pyts/tsparser`.

## Installation

```bash
pip install pytsast
```

## Usage

### Basic Example

```python
from pytsast import factory as ts

# Create a simple identifier
identifier = ts.createIdentifier("myVariable")

# Serialize to JSON
json_output = identifier.serialize()
print(json_output.model_dump_json(indent=2))
```

### Creating Complex Structures

```python
from pytsast import factory as ts

# Create an import declaration
import_decl = ts.createImportDeclaration(
    None,
    ts.createImportClause(
        None,
        ts.createIdentifier("zod"),
        ts.createNamedImports([
            ts.createImportSpecifier(
                False, None, ts.createIdentifier("output")
            )
        ]),
    ),
    ts.createStringLiteral("zod"),
    None,
)

# Create a function declaration
func_decl = ts.createFunctionDeclaration(
    None,
    None,
    ts.createIdentifier("greet"),
    None,
    [
        ts.createParameterDeclaration(
            None, None, ts.createIdentifier("name"), None,
            ts.createTypeReferenceNode(ts.createIdentifier("string"), None), None
        )
    ],
    ts.createTypeReferenceNode(ts.createIdentifier("string"), None),
    ts.createBlock([
        ts.createReturnStatement(
            ts.createBinaryExpression(
                ts.createStringLiteral("Hello, "),
                ts.createToken(ts.SyntaxKind.PlusToken),
                ts.createIdentifier("name")
            )
        )
    ], True)
)

# Serialize both
print("Import:", import_decl.serialize().model_dump_json())
print("Function:", func_decl.serialize().model_dump_json())
```

### Low-Level Node Creation

```python
from pytsast.core import Node
from pytsast.nodes.misc import Parameter

# Create nodes directly
param = Parameter(
    decorators=None,
    modifiers=None,
    dot_dot_dot_token=None,
    name=ts.createIdentifier("arg"),
    question_token=None,
    type_annotation=ts.createTypeReferenceNode(ts.createIdentifier("number"), None),
    initializer=None
)
```

## API

### Factory Functions

The `factory` module mirrors TypeScript's `ts.factory` API:

- `createIdentifier(text: str)` - Create identifier node
- `createStringLiteral(text: str)` - Create string literal
- `createNumericLiteral(value: str | int | float)` - Create numeric literal
- `createImportDeclaration(decorators, modifiers, import_clause, module_specifier, assert_clause)` - Create import statement
- `createFunctionDeclaration(decorators, modifiers, asterisk_token, name, type_parameters, parameters, type, body)` - Create function declaration
- `createClassDeclaration(decorators, modifiers, name, type_parameters, heritage_clauses, members)` - Create class declaration
- `createVariableStatement(modifiers, declaration_list)` - Create variable statement
- `createTypeAliasDeclaration(modifiers, name, type_parameters, type)` - Create type alias
- And many more...

### Core Classes

- `Node` - Base AST node class with serialization
- `SyntaxKind` - Enum of TypeScript syntax kinds
- `NodeFlags` - Node flags enum

### Node Types

- `Statement` - Base for statements (function declarations, etc.)
- `Expression` - Base for expressions (identifiers, literals, etc.)
- `Declaration` - Base for declarations
- `TypeNode` - Base for type annotations

## Serialization Format

Nodes serialize to JSON objects that can be consumed by TypeScript parsers:

```json
{
  "type": "factory",
  "name": "createIdentifier",
  "args": [
    {
      "type": "literal",
      "value": "myVariable"
    }
  ]
}
```

### Node Types

- **literal**: `{ "type": "literal", "value": null | boolean | string }`
- **number**: `{ "type": "number", "value": number | string }`
- **undefined**: `{ "type": "undefined" }`
- **factory**: `{ "type": "factory", "name": string, "args": SerializedNode[] }`

## Integration with tsparser

pytsast is designed to work with `@pyts/tsparser` to generate actual TypeScript code:

```python
# Python side (pytsast)
from pytsast import factory as ts
import json

node = ts.createIdentifier("hello")
json_str = json.dumps(node.serialize().model_dump())

# Send json_str to TypeScript side
```

```typescript
// TypeScript side (@pyts/tsparser)
import { parseAndPrint } from '@pyts/tsparser';

const jsonFromPython = '...'; // JSON from Python
const tsCode = parseAndPrint(jsonFromPython);
console.log(tsCode); // hello
```

### Complete Example

```python
# Python: Generate a complete TypeScript interface
from pytsast import factory as ts
import json

interface = ts.createInterfaceDeclaration(
    None,  # decorators
    None,  # modifiers
    ts.createIdentifier("User"),
    None,  # type parameters
    None,  # heritage clauses
    [
        ts.createPropertySignature(
            None,  # modifiers
            ts.createIdentifier("id"),
            None,  # question token
            ts.createTypeReferenceNode(ts.createIdentifier("number"), None)
        ),
        ts.createPropertySignature(
            None,
            ts.createIdentifier("name"),
            None,
            ts.createTypeReferenceNode(ts.createIdentifier("string"), None)
        )
    ]
)

json_output = json.dumps(interface.serialize().model_dump(), indent=2)
print(json_output)
```

```typescript
// TypeScript: Parse and generate code
import { parseAndPrint } from '@pyts/tsparser';

const jsonFromPython = `...`; // The JSON above
const tsCode = parseAndPrint(jsonFromPython);
console.log(tsCode);
// Output:
// interface User {
//     id: number;
//     name: string;
// }
```

## Architecture

- `pytsast/core/` - Base types, serialization, and syntax kinds
- `pytsast/nodes/` - AST node definitions and implementations
- `pytsast/factory.py` - Factory functions (mirrors `ts.factory`)
