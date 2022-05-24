from __future__ import annotations

from dataclasses import KW_ONLY, InitVar, dataclass, field
from typing import Any, Optional, Tuple


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
class Expression(TrackPosition): 
    _ : KW_ONLY
    is_assignable: bool = False
    expr_type: Optional[VariableType] = field(init=False, default=None)

    
@dataclass
class LitInt(Expression):
    value: str

@dataclass
class LitFloat(Expression):
    value: str

@dataclass
class LitChar(Expression):
    value: str

@dataclass
class LitBool(Expression):
    value: str

@dataclass
class ID(Expression):
    value: str

    def __post_init__(self, s: Optional[TrackPosition], p: Optional[Any]):
        self.is_assignable = True
        return super().__post_init__(s, p)


@dataclass
class Program:
    main_algorithm: MainAlgorithm
    sub_algorithms_list: list[SubAlgorithm]

@dataclass
class MainAlgorithm:
    name: ID
    type_definitions: list
    variable_declarations: list[VariableDeclaration]
    statements: list[Statement]


@dataclass
class SubAlgorithm:
    name: ID
    inputs: list[VariableDeclaration]
    outputs: list[VariableDeclaration]
    variable_declarations: list[VariableDeclaration]
    statements: list[Statement]


@dataclass
class VariableDeclaration:
    name: ID
    type: VariableType

class VariableType(TrackPosition): pass

@dataclass
class BaseType(VariableType):
    value: str

    def __str__(self) -> str:
        return f"<{self.value}>"

@dataclass
class PtrType(VariableType):
    type: VariableType

    def __str__(self) -> str:
        return f"<Pointeur sur {self.type}>"

@dataclass
class TableType(VariableType):
    ranges: list[TableRange]
    type: VariableType

    def __str__(self) -> str:
        return f"<Tableau[{', '.join(str(range) for range in self.ranges)}] de {self.type}>"
        
@dataclass
class TableRange:
    start: LitInt
    end: Optional[LitInt]

    def __str__(self) -> str:
        return f"{self.start.value}..{self.end.value if self.end is not None else ''}"

    def is_equivalent_to(self, other: TableRange) -> bool:
        if int(self.start.value) != int(other.start.value):
            return False
        
        # Yes this is weird, but it works. First I check if both ends are None, in which case we know they are equivalent. 
        if self.end is None or other.end is None:
            return True

        return int(self.end.value) == int(other.end.value)



class Statement(TrackPosition): pass

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
    operator: Operator

    
class UnaryPlus(UnaryOperation): pass
class UnaryMinus(UnaryOperation): pass
class UnaryDereference(UnaryOperation):
    def __post_init__(self, s: Optional[TrackPosition], p: Optional[Any]):
        self.is_assignable = self.expression.is_assignable
        return super().__post_init__(s, p)

class UnaryPointer(UnaryOperation): pass
class UnaryNot(UnaryOperation): pass


@dataclass
class BinaryOperation(Expression): 
    left: Expression
    right: Expression
    operator: Operator

@dataclass
class Operator(TrackPosition):
    operator: str

class BinaryPlus(BinaryOperation): pass
class BinaryMinus(BinaryOperation): pass
class BinaryTimes(BinaryOperation): pass
class BinaryDivide(BinaryOperation): pass
class BinaryModulo(BinaryOperation): pass
class BinaryEq(BinaryOperation): pass
class BinaryAnd(BinaryOperation): pass
class BinaryOr(BinaryOperation): pass
class BinaryLT(BinaryOperation): pass
class BinaryGT(BinaryOperation): pass
class BinaryLTE(BinaryOperation): pass
class BinaryGTE(BinaryOperation): pass

@dataclass
class AttributeExpression(Expression):
    expression: Expression
    attribute: ID

    def __post_init__(self, s: Optional[TrackPosition], p: Optional[Any]):
        self.is_assignable = True
        return super().__post_init__(s, p)

@dataclass
class TableExpression(Expression):
    table_expression: Expression
    indexes: list[Expression]

    def __post_init__(self, s: Optional[TrackPosition], p: Optional[Any]):
        self.is_assignable = True
        return super().__post_init__(s, p)


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
    step: Optional[LitInt]
    statements: list[Statement]

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

@dataclass
class CustomTypeDefinition:
    name: ID
    attributes: list[VariableDeclaration]