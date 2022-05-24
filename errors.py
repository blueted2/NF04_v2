from typing import Optional
from ast_nodes import ID, BaseType, VariableType, Expression, LitInt, Operator, SubAlgorithm, TrackPosition
from lexer import MyLexer
from utils import get_column, get_source_code_line


def get_line_columns_str(lineno, cols: list[int]):
    if len(cols) == 1:
        return f"Ligne {lineno}, colonne {cols[0]}\n"

    return f"Ligne {lineno}, colonnes " + ", ".join([f"{col}" for col in cols[:-1]]) + f" et {cols[-1]}\n"

def get_arrows_line(lineno, cols):
    num_len = len(str(lineno))
    result = " " * num_len + " | "
    current_col = 0
    for col in sorted(cols):
        result += " " * (col-current_col-1) + "^"
        current_col = col

    result += "\n"
    return result

def set_source_code(source_code: str):
    TokenSyntaxError._source_code = source_code
    NodeSyntaxError._source_code = source_code
    SemanticError._source_code = source_code
    LitCharError._source_code = source_code


def error_header_string(source_code, lexpos, lineno) -> str:
    result = ""
    column = get_column(source_code, lexpos)
    source_code_line = get_source_code_line(source_code, lexpos)

    result += f"{get_line_columns_str(lineno, [column])}"
    result += f"  {lineno} | {source_code_line} \n"
    result += f"  {get_arrows_line(lineno, [column])}"

    return result

class TokenSyntaxError:
    _source_code: str = ""
    def __init__(self, token, expected: Optional[str] = None, error_type: Optional[str] = None, details: Optional[str] = None):
        self.token = token
        self.expected = expected
        self.error_type = error_type
        self.details = details
        self.source_code = TokenSyntaxError._source_code

    def __str__(self) -> str:
        result = ""

        opt_kw_str         = "mot clé " if self.token.type in MyLexer.reserved else ""
        type_str           = f"'{self.token.type}' "
        opt_value_str      = f"({repr(self.token.value)}) " if str(self.token.type) != str(self.token.value) else ""

        opt_error_type_str = f" -> {self.error_type} " if self.error_type is not None else ""

        result += error_header_string(self.source_code, self.token.lexpos, self.token.lineno)
        result += f"Erreur de syntaxe: {opt_kw_str}{type_str}{opt_value_str}inattendu{opt_error_type_str}"
        
        if self.details is not None:
            result += f"\n{self.details}"

        if self.expected is not None:
            result += f"\n -> Attendu: {self.expected}"

        return result

class LitCharError:
    _source_code: str = ""
    def __init__(self, lexpos: int, lineno: int) -> None:
        self.lexpos = lexpos
        self.lineno = lineno
        self.source_code = LitCharError._source_code

    def __str__(self) -> str:
        result = ""
        
        result += error_header_string(self.source_code, self.lexpos, self.lineno)
        result += f"Erreur de syntaxe: Caractère litéral mal formé"

        return result
    

class NodeSyntaxError:
    _source_code = ""
    def __init__(self, node: TrackPosition, details: Optional[str] = None):
        self.node = node
        self.details = details
        self.source_code = TokenSyntaxError._source_code

    def __str__(self) -> str:
        result = ""

        result += error_header_string(self.source_code, self.node.lexpos, self.node.lineno)
        result += f"Erreur de syntaxe: {self.details}"

        return result



class SemanticError:
    _source_code: str = ""
    def __init__(self):
        self.source_code = SemanticError._source_code

class DoubleLineError(SemanticError):
    def __init__(self, original: TrackPosition, new: TrackPosition, details: str):
        super().__init__()
        self.original = original
        self.new = new
        self.details = details

    def __str__(self) -> str:
        result = ""

        if self.original.lineno != self.new.lineno:
            result += error_header_string(self.source_code, self.original.lexpos, self.original.lineno)
            result += error_header_string(self.source_code, self.new.lexpos, self.new.lineno)
        else:
            lineno = self.original.lineno
            lexpos = self.original.lexpos

            original_col = get_column(self.source_code, lexpos)
            new_col = get_column(self.source_code, self.new.lexpos)
            cols = [original_col, new_col]

            source_code_line = get_source_code_line(self.source_code, lexpos)

            result += f"{get_line_columns_str(lineno, cols)}"
            result += f"  {lineno} | {source_code_line} \n"
            result += f"  {get_arrows_line(lineno, cols)}"

        result += f"Erreur sémantique: {self.details}"

        return result

class VariableRedeclarationError(DoubleLineError):
    def __init__(self, original_id: ID, new_id: ID):
        super().__init__(original_id, new_id, f"Redéclaration de la variable '{original_id.value}'")

class SubAlgoRedefinitionError(DoubleLineError):
    def __init__(self, original_sub_algo: SubAlgorithm, new_sub_algo: SubAlgorithm):
        super().__init__(original_sub_algo.name, new_sub_algo.name, f"Redéfinition du sous-algorithme '{original_sub_algo.name.value}'")

class TypeRedefinitionError(DoubleLineError):
    def __init__(self, original: ID, new: ID):
        super().__init__(original, new, f"Redéfinition du type '{original.value}'")

class AttributeRedeclarationError(DoubleLineError):
    def __init__(self, original: ID, new: ID, custom_type_name: str):
        super().__init__(original, new, f"Redéclaration de l'attribut '{original.value}' dans le type '{custom_type_name}'")

class IdRedefinitionError(DoubleLineError):
    def __init__(self, original: ID, new: ID):
        super().__init__(original, new, details=f"Redéfinition de l'identifiant '{original.value}'")

class StandardSemanticError(SemanticError):
    def __init__(self, bad_node: TrackPosition, details: str, description: Optional[str] = None):
        super().__init__()
        
        self.bad_node = bad_node
        self.details = details
        self.description = description

    def __str__(self) -> str:
        result = ""
        result += error_header_string(self.source_code, self.bad_node.lexpos, self.bad_node.lineno)
        result += f"Erreur sémantique: {self.details}"

        if self.description is not None:
            result += f"\n -> {self.description}"

        return result

class TableRangeInvalidEndError(StandardSemanticError):
    def __init__(self, bad_node: LitInt, description: Optional[str] = None):
        super().__init__(bad_node, f"Indice de fin '{bad_node.value}' incorrect", description)

class TableEndNotDefinedForVariableError(StandardSemanticError):
    def __init__(self, start_expression: Expression):
        super().__init__(start_expression, f"L'indice de fin de tableau doit être défini")

class NonUniqueOutputFunctionExpressionError(StandardSemanticError):
    def __init__(self, function_call_id: ID, expected_outputs: int):
        super().__init__(function_call_id, f"Un algorithme utilisé comme expression doit avoir exactement un paramètre de sortie ({expected_outputs} attendus)")


class UnknownBaseTypeError(StandardSemanticError):
    def __init__(self, bad_base_type: BaseType, description: Optional[str] = None):
        super().__init__(bad_base_type, f"Type '{bad_base_type.value}' inconnu", description)

class InvalidBaseTypeError(StandardSemanticError):
    def __init__(self, bad_base_type: ID, description: Optional[str] = None):
        super().__init__(bad_base_type, f"Type de base '{bad_base_type.value}' incorrect", description)

class UnknownIDError(StandardSemanticError):
    def __init__(self, bad_id: ID):
        super().__init__(bad_id, f"Identifiant '{bad_id.value}' inconnu")


class UndeclaredVariableError(StandardSemanticError):
    def __init__(self, bad_id: ID):
        super().__init__(bad_id, details = f"Variable '{bad_id.value}' non déclarée")

class UndefinedFunctionError(StandardSemanticError):
    def __init__(self, bad_id: ID):
        super().__init__(bad_id, f"Sous-algorithme '{bad_id.value}' non déclaré")


class MultiSemanticError(SemanticError):
    def __init__(self, nodes: list[TrackPosition], details: Optional[str] = None, description: Optional[str] = None):
        super().__init__()
        self.nodes = nodes        
        self.details = details
        self.description = description

    def __str__(self) -> str:
        result = ""
        lineno = self.nodes[0].lineno
        lexpos = self.nodes[0].lexpos
        source_code = self.source_code
        cols = sorted([get_column(source_code, node.lexpos) for node in self.nodes])


        line_columns_str = f"Ligne {lineno}, colonnes " + ", ".join([f"{col}" for col in cols[:-1]]) + f" et {cols[-1]}\n"
        result += line_columns_str

        source_code_line = get_source_code_line(source_code, lexpos)
        result += f"  {lineno} | {source_code_line} \n"

        arrows_line = get_arrows_line(self.nodes[0].lineno, cols)
        result += f"  {arrows_line}"

        result += f"Erreur sémantique: {self.details}"

        if self.description is not None:
            result += f"\n -> {self.description}"

        return result

class IncompatibleAssignmentTypesError(MultiSemanticError):
    def __init__(self, left_expression: Expression, left_type: VariableType, right_expression: Expression, right_type: VariableType):
        details = f"Incompatibilité du type d'affectation : '{left_type}' <-- '{right_type}'"
        super().__init__([left_expression, right_expression], details)


class IncompatibleInputTypeError(StandardSemanticError):
    def __init__(self, input_expression: Expression, input_type: VariableType, expected_input_type: VariableType):
        details = f"Incompatibilité du type de paramètre d'entrée ({input_type}) --> '{expected_input_type}' attendu"
        super().__init__(input_expression, details)

class IncompatibleOutputTypeError(StandardSemanticError):
    def __init__(self, output_expression: Expression, output_type: VariableType, expected_output_type: VariableType):
        details = f"Incompatibilité du type de paramètre de sortie ({output_type}) --> '{expected_output_type}' attendu"
        super().__init__(output_expression, details)

class UnmatchedNumberOfInputsError(StandardSemanticError):
    def __init__(self, call_id: ID, received_num: int, expected_num: int):
        super().__init__(call_id, f"Mauvais nombre de paramètres d'entrées ({received_num}) --> {expected_num} {'attendus' if expected_num > 1 else 'attendu'}")

class UnmatchedNumberOfOutputsError(StandardSemanticError):
    def __init__(self, call_id: ID, received_num: int, expected_num: int):
        super().__init__(call_id, f"Mauvais nombre de paramètres de sortie ({received_num}) --> {expected_num} {'attendus' if expected_num > 1 else 'attendu'}")

class UnmatchedTableIndexesError(StandardSemanticError):
    def __init__(self, table_expression: Expression, table_type: VariableType, received_num: int, expected_num: int):
        super().__init__(table_expression, f"Mauvais nombre d'indices ({received_num}) pour tableau ({table_type}) --> {expected_num} {'attendus' if expected_num > 1 else 'attendu'}")


class TableAssignmentError(StandardSemanticError):
    def __init__(self, left: Expression, left_type):
        super().__init__(left, details=f"Pas possible de directement affecter une valeur à un tableau ({left_type}) dans sa totalité")

class NonAssignableExpressionError(StandardSemanticError):
    def __init__(self, expression: Expression):
        super().__init__(expression, f"Expression non affectable")

class NonTableElementAccessError(StandardSemanticError):
    def __init__(self, bad_expression: Expression, bad_expression_type: VariableType):
        super().__init__(bad_expression, details=f"Accès d'élément dans une expression ({bad_expression_type}) qui n'est pas un tableau")

class NonIntegerIndexError(StandardSemanticError):
    def __init__(self, index: Expression, index_type: VariableType):
        super().__init__(index, f"Type d'expression indice ({index_type}) doit être de type <entier>")

class NonIntegerIterationVariableError(StandardSemanticError):
    def __init__(self, iter_var: ID, iter_var_type: VariableType):
        super().__init__(iter_var, f"Type de la variable d'itération ({iter_var_type}) doit être de type <entier>")

class NonIntegerStartError(StandardSemanticError):
    def __init__(self, start: Expression, start_type: VariableType):
        super().__init__(start, f"Type d'expression début d'itération ({start_type}) doit être de type <entier>")

class NonIntegerEndError(StandardSemanticError):
    def __init__(self, end: Expression, end_type: VariableType):
        super().__init__(end, f"Type d'expression fin d'itération ({end_type}) doit être de type <entier>")

class NonBooleanWhileConditionError(StandardSemanticError):
    def __init__(self, bad_condition: Expression, bad_condition_type: VariableType):
        super().__init__(bad_condition, f"Condition de boucle ({bad_condition_type}) doit être de type {BaseType('booléen')}")

class NonBooleanIfConditionError(StandardSemanticError):
    def __init__(self, bad_condition: Expression, bad_condition_type: VariableType):
        super().__init__(bad_condition, f"Condition ({bad_condition_type}) doit être de type {BaseType('booléen')}")

class NonCustomTypeAttributeAccessError(StandardSemanticError):
    def __init__(self, main_expression: Expression, main_expression_type: VariableType):
        super().__init__(main_expression, f"Access d'attribut d'une expression ({main_expression_type}) qui n'est pas un article")

class TableIndexWrongTypeError(StandardSemanticError):
    def __init__(self, bad_index: Expression, bad_index_type: VariableType):
        super().__init__(bad_index, f"Expression indice doit être de type <entier> et non {bad_index_type}")

class IncompatibleExpressionTypeError(StandardSemanticError):
    def __init__(self, bad_expression: Expression, details: str, description: Optional[str] = None):
        super().__init__(bad_expression, details, description)

class InvalidBinaryOperationTermType(MultiSemanticError):
    def __init__(self, term: Expression, term_type: VariableType, operator: Operator, description: Optional[str] = None):
        if term.lexpos < operator.lexpos:
            left = term
            right = operator
        else:
            left = operator
            right = term

        super().__init__([left, right], details=f"Type d'expression invalid ({term_type}) pour opération '{operator.operator}'", description=description)

class InvalidUnaryOperationExpressionTypeError(StandardSemanticError):
    def __init__(self, expression: Expression, expression_type: VariableType, operator: Operator):
        super().__init__(expression, f"Type d'expression invalid ({expression_type}) pour opérateur '{operator.operator}'")

class NonPointerDereferenceError(StandardSemanticError):
    def __init__(self, expression: Expression, expression_type: VariableType, ):
        super().__init__(expression, f"Deréférence d'une expression ({expression_type}) qui n'est pas un pointer")

class NonBooleanUnaryNotError(StandardSemanticError):
    def __init__(self, bad_condition: Expression, bad_condition_type: VariableType):
        super().__init__(bad_condition, f"Expression ({bad_condition_type}) doit être de type {BaseType('booléen')} après 'non'")

    
class DifferentTypesComparisonError(MultiSemanticError):
    def __init__(self, left: Expression, left_type: VariableType, right: Expression, right_type: VariableType, operator: Operator):
        super().__init__([left, right, operator], f"Pas possible de comparer deux expressions de types différents: '{left_type}' '{operator.operator}' '{right_type}'")

class TypeDefinitionRecursionError(StandardSemanticError):
    def __init__(self, type_name: ID):
        super().__init__(type_name, f"Récursion dans la définition de l'article '{type_name.value}'")

class InvalidAttributError(MultiSemanticError):
    def __init__(self, main_expression: Expression, main_expression_type: VariableType, attribute: ID):
        super().__init__([main_expression, attribute], f"L'expression de type {main_expression_type} n'a pas d'attribut '{attribute.value}'")

class CKeywordError(StandardSemanticError):
    def __init__(self, bad_id: ID):
        super().__init__(bad_id, f"'{bad_id.value}' est déja un mot clé en C")