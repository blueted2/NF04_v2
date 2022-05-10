from distutils.log import error
from typing import Optional
from ast_nodes import ID, ASTNode, LitInt, TrackPosition
from lexer import MyLexer
from utils import get_column, get_source_code_line


def line_column_str(lineno, col):
    return f"Ligne {lineno}, colonne {col} \n"

def arrow_line(lineno, col):
    num_len = len(str(lineno))
    return " " * num_len + " | " + " " * (col - 1) + "^ \n"

def set_source_code(source_code: str):
    e_SyntaxError._source_code = source_code
    SemanticError._source_code = source_code

class e_SyntaxError:
    _source_code: str = ""
    def __init__(self, token, expected: Optional[str] = None, error_type: Optional[str] = None, details: Optional[str] = None):
        self.token = token
        self.expected = expected
        self.error_type = error_type
        self.details = details
        self.source_code = e_SyntaxError._source_code

    def __str__(self) -> str:
        result = ""

        token_column = get_column(self.source_code, self.token.lexpos)
        source_code_line = get_source_code_line(self.source_code, self.token.lexpos)

        result += f"{line_column_str(self.token.lineno, token_column)}"
        result += f"  {self.token.lineno} | {source_code_line} \n"
        result += f"  {arrow_line(self.token.lineno, token_column)}"

        opt_kw_str         = "mot clé " if self.token.type in MyLexer.reserved else ""
        type_str           = f"'{self.token.type}' "
        opt_value_str      = f"({repr(self.token.value)}) " if str(self.token.type) != str(self.token.value) else ""
        opt_error_type_str = f" -> {self.error_type} " if self.error_type is not None else ""

        result += f"Erreur de syntaxe: {opt_kw_str}{type_str}{opt_value_str}inattendu{opt_error_type_str}"
        
        if self.details is not None:
            result += f"\n{self.details}"

        if self.expected is not None:
            result += f"\n -> Attendu: {self.expected}"

        return result


class SemanticError:
    _source_code: str = ""
    def __init__(self):
        self.source_code = SemanticError._source_code

class VariableRedefinitionError(SemanticError):
    def __init__(self, bad_node: TrackPosition, column: int, source_code_line: Optional[str] = None, description: Optional[str] = None):
        super().__init__()


class TableRangeError(SemanticError):
    def __init__(self, bad_node: LitInt, error_type: str, description: Optional[str] = None):
        super().__init__()
        
        self.bad_node = bad_node
        self.error_type = error_type
        self.description = description

    def __str__(self) -> str:
        result = ""

        node_column = get_column(self.source_code, self.bad_node.lexpos)
        source_code_line = get_source_code_line(self.source_code, self.bad_node.lexpos)

        result += f"{line_column_str(self.bad_node.lineno, node_column)}"

        result += f"  {self.bad_node.lineno} | {source_code_line} \n"
        result += f"  {arrow_line(self.bad_node.lineno, node_column)}"
            
        result += f"Erreur sémantique: {self.error_type}"

        if self.description is not None:
            result += f"\n -> {self.description}"

        return result

class TableRangeInvalidEndError(TableRangeError):
    def __init__(self, bad_node: LitInt, description: Optional[str] = None):
        super().__init__(bad_node, f"Indice de fin '{bad_node.value}' incorrect", description)