from typing import Any

from evalis.antlr4_adapter import parse_expression_tree
from evalis.ast import AstBuilder, EvalisNode
from evalis.eval import Evaluator
from evalis.types import EvaluatorOptions


def parse_ast(expression: str) -> EvalisNode:
    tree = parse_expression_tree(expression)

    builder = AstBuilder()
    return builder.visit(tree)


def evaluate_ast(
    node: EvalisNode,
    context: dict[str, Any] = {},
    options: EvaluatorOptions = EvaluatorOptions(),
) -> Any:
    evaluator = Evaluator(options)
    result = evaluator.evaluate(node, context)

    return result


def evaluate_expression(
    expression: str,
    context: dict[str, Any] = {},
    options: EvaluatorOptions = EvaluatorOptions(),
) -> Any:
    ast = parse_ast(expression)

    return evaluate_ast(ast, context, options)
