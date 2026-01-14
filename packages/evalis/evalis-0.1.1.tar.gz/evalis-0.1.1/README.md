# Evalis

A secure, user-friendly expression evaluator for Python.

> **Early Release**: This is an early release with core functionality. More features are in active development. Check the [main project](https://github.com/GojiYoji/evalis) for roadmap and updates.

## Installation

```bash
pip install evalis
```

## Quick Start

```python
from evalis import evaluate_expression

context = {"a": {"b": 5}}
value = evaluate_expression("a.b + 2", context)

print(value)  # 7
```

## Features

- **Safe evaluation** - No `eval()`. No access to global namespace.
- **Simple syntax** - Familiar expressions with property access, operators, and comprehensions.
- **Type-safe** - Full type hints included for static type checking.

## Supported Operations

- **Arithmetic**: `+`, `-`, `*`, `/`
- **Comparison**: `==`, `!=`, `<`, `<=`, `>`, `>=`
- **Logical**: `and`, `or`, `not`
- **Property access**: `obj.property`, `obj['key']`
- **Array access**: `arr[0]`
- **List comprehensions**: `[x * 2 for x in numbers]`
- **Membership**: `x in collection`

## API Reference

### `evaluate_expression(expression, context, options)`

Evaluates an expression string with the given context.

**Parameters:**
- `expression` (str): The expression to evaluate
- `context` (dict): Variable context for the expression
- `options` (EvaluatorOptions, optional): Evaluation options

**Returns:** The evaluated result

**Example:**
```python
from evalis import evaluate_expression

result = evaluate_expression("x * 2", {"x": 21})
# result = 42
```

### `parse_ast(expression)`

Parses an expression into an AST without evaluating it.

**Parameters:**
- `expression` (str): The expression to parse

**Returns:** An AST node representing the expression

**Example:**
```python
from evalis import parse_ast

ast = parse_ast("a + b")
# Returns: BinaryOpNode(op=BinaryOpType.ADD, left=..., right=...)
```

### `evaluate_ast(node, context, options)`

Evaluates a pre-parsed AST node.

**Parameters:**
- `node` (EvalisNode): The AST node to evaluate
- `context` (dict): Variable context for evaluation
- `options` (EvaluatorOptions, optional): Evaluation options

**Returns:** The evaluated result

**Example:**
```python
from evalis import parse_ast, evaluate_ast

ast = parse_ast("x + 1")
result = evaluate_ast(ast, {"x": 5})
# result = 6
```

### `EvaluatorOptions`

Configuration options for evaluation.

**Fields:**
- `should_null_on_bad_access` (bool, default=False): Return `None` instead of raising errors on invalid property access

**Example:**
```python
from evalis import evaluate_expression, EvaluatorOptions

options = EvaluatorOptions(should_null_on_bad_access=True)
result = evaluate_expression("foo.missing", {}, options)
# result = None (instead of raising an error)
```

## More Information

This is the Python implementation of Evalis. For more details about the project:

- [Main Project](https://github.com/GojiYoji/evalis)
- [Architecture](https://github.com/GojiYoji/evalis/blob/main/docs/architecture.md)
- [TypeScript Implementation](https://github.com/GojiYoji/evalis/tree/main/typescript)

## License

MIT
