from __future__ import annotations

from dataclasses import KW_ONLY, InitVar, dataclass, field
from email.policy import default
from typing import Any, Optional, Tuple


class ASTNode: pass

@dataclass(kw_only=True)
class TrackPosition:
    lineno: int = -1
    lexpos: int = -1

    s: InitVar[Optional[TrackPosition]] = None
    p: InitVar[Optional[Any]] = None

    def __post_init__(self, s: Optional[TrackPosition], p: Optional[Any]):
        # if p is None and s is None:
        #     raise TypeError('Need start node or parser object to determine beginning')

        if p is not None and s is not None:
            raise TypeError('Can\'t have both p and s')

        if s is not None:
            self.lineno = s.lineno
            self.lexpos = s.lexpos
            return
        
        # Explicit check for type checking purposesa
        # In theory it shouldn't be necessary
        if p is not None:
            self.lineno = p.lineno(1)
            self.lexpos = p.lexpos(1)

@dataclass
class Expression(ASTNode, TrackPosition): pass
    
@dataclass
class LitInt(Expression):
    value: int

@dataclass
class LitFloat(Expression):
    value: float

@dataclass
class ID(ASTNode, TrackPosition):
    value: str


@dataclass
class Program(ASTNode):
    main_algorithm: MainAlgorithm
    sub_algorithms_list: list[SubAlgorithm]

@dataclass
class MainAlgorithm(ASTNode):
    name: ID
    type_definitions: list
    variable_declarations: list[VariableDeclarationLine]
    statements: list[Statement]


@dataclass
class SubAlgorithm(ASTNode):
    name: ID
    inputs: list[VariableDeclarationLine]
    outputs: list[VariableDeclarationLine]
    variable_declarations: list[VariableDeclarationLine]
    statements: list[Statement]

@dataclass
class VariableDeclarationLine(ASTNode):
    names: list[ID]
    type: ComplexType


class ComplexType(ASTNode, TrackPosition): pass

@dataclass
class BaseType(ComplexType):
    name: ID

@dataclass
class PtrType(ComplexType):
    type: ComplexType

@dataclass
class TableType(ComplexType):
    ranges: list[Tuple[LitInt, Optional[LitInt]]]
    type: ComplexType


class Statement(ASTNode, TrackPosition): pass

@dataclass
class AssignmentStatement(Statement):
    left: Expression
    right: Expression

@dataclass
class ExpressionStatement(Statement):
    expression: Expression



@dataclass
class SubExpression(Expression):
    expression: Expression


@dataclass
class UnaryOperation(Expression):
    expression: Expression
    
class UnaryPlus(UnaryOperation): pass
class UnaryMinus(UnaryOperation): pass
class UnaryDereference(UnaryOperation): pass
class UnaryPointer(UnaryOperation): pass
class UnaryNot(UnaryOperation): pass


@dataclass
class BinaryOperation(Expression): 
    left: Expression
    right: Expression

class BinaryPlus(BinaryOperation): pass
class BinaryMinus(BinaryOperation): pass
class BinaryTimes(BinaryOperation): pass
class BinaryDivide(BinaryOperation): pass
class BinaryModulo(BinaryOperation): pass
class BinaryAnd(BinaryOperation): pass
class BinaryOr(BinaryOperation): pass
class BinaryLT(BinaryOperation): pass
class BinaryGT(BinaryOperation): pass
class BinaryLTE(BinaryOperation): pass
class BinaryGTE(BinaryOperation): pass

@dataclass
class AttributExpression(Expression):
    expression: Expression
    attribut: ID

@dataclass
class TableExpression(Expression):
    expression: Expression
    index: Expression


@dataclass
class FunctionExpression(Expression):
    name: ID
    inputs: list[Expression]


@dataclass
class FunctionStatement(Statement):
    name: ID
    inputs: list[Expression]
    outputs: list[ID]


@dataclass
class PourStatement(Statement):
    variable: ID
    start: Expression
    end: Expression
    statements: list[Statement]
    _: KW_ONLY 
    step: Expression = LitInt(1)

@dataclass
class TantQueStatement(Statement):
    condition: Expression
    statements: list[Statement]

@dataclass
class SiStatement(Statement):
    conditional_blocks: list[ConditionalBlock]
    default_block: list[Statement] = field(default_factory=list)
    

@dataclass
class ConditionalBlock:
    condition: Expression
    statements: list[Statement]