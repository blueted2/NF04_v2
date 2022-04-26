from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


# We make this dataclass keyword-only, and give default values to span and linespan.
@dataclass(kw_only=True)
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    main_algorithm: MainAlgorithm
    sub_algorithms_list: list[SubAlgorithm]
    type_definitions: list

@dataclass
class MainAlgorithm(ASTNode):
    name: str
    variable_declarations: list[VariableDeclarationLine]
    statements: list

@dataclass
class SubAlgorithm(ASTNode):
    name: str
    variable_declarations: list[VariableDeclarationLine]
    inputs: list[VariableDeclarationLine]
    outputs: list[VariableDeclarationLine]
    statements: list

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
class PtrType(ComplexType):
    type: ComplexType

@dataclass
class TableType(ComplexType):
    type: ComplexType
    start: int
    end: int

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