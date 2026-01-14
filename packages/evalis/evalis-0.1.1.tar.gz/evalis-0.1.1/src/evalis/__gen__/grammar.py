from dataclasses import dataclass
from enum import Enum

RESERVED_KEYWORDS = [
    "not"
    "and"
    "or"
    "null"
    "true"
    "false"
    "in"
    "for"
]
class BinaryOpType(Enum):
    MULTIPLY = "*"
    DIVIDE = "/"
    ADD = "+"
    SUBTRACT = "-"
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    EQUALS = "=="
    NOT_EQUALS = "!="
    AND = "and"
    OR = "or"
    IN = "in"

class UnaryOpType(Enum):
    NOT = "not"

