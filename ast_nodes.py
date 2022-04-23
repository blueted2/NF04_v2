from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


# We make this dataclass keyword-only, and give default values to span and linespan.
@dataclass(kw_only=True)
class ASTNode:
    lineno: Optional[int] = None


@dataclass
class Program(ASTNode):
    variable_declarations: list[VariableDeclarationLine]
    program_statements: list


@dataclass
class VariableDeclarationLine(ASTNode):
    names: list[str]
    type: ComplexType


@dataclass
class ComplexType(ASTNode):
    base_type: str
    modifiers: list[TypeModifier]


@dataclass 
class TypeModifier(ASTNode): pass


@dataclass
class PtrTypeModifier(TypeModifier): pass


@dataclass
class TableTypeModifier(TypeModifier):
    start: int
    end: int


@dataclass
class LitInt(ASTNode):
    value: int


@dataclass
class LitFloat(ASTNode):
    value: float