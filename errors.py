from distutils.log import error
from typing import Optional
from ast_nodes import ID, ASTNode, LitInt, TrackPosition
from lexer import MyLexer

def line_column_str(lineno, col):
    return f"Ligne {lineno}, colonne {col} \n"

def arrow_line(lineno, col):
    num_len = len(str(lineno))
    return " " * num_len + " | " + " " * (col - 1) + "^ \n"

class e_SyntaxError:

    def __init__(self, token, column, expected: Optional[str] = None, source_code_line: Optional[str] = None, error_type: Optional[str] = None, details: Optional[str] = None):
        self.token = token
        self.column = column
        self.expected = expected
        self.source_code_line = source_code_line
        self.error_type = error_type
        self.details = details



    def __str__(self) -> str:
        result = ""
        result += f"{line_column_str(self.token.lineno, self.column)}"

        if self.source_code_line is not None:
            result += f"  {self.token.lineno} | {self.source_code_line} \n"
            result += f"  {arrow_line(self.token.lineno, self.column)}"

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
    def __init__(self, bad_node: TrackPosition, column: int, source_code_line: Optional[str] = None, description: Optional[str] = None):
        self.bad_node = bad_node
        self.column = column
        self.source_code_line = source_code_line
        self.description = description

class VariableRedefinitionError(SemanticError):
    def __init__(self, bad_node: TrackPosition, column: int, source_code_line: Optional[str] = None, description: Optional[str] = None):
        super().__init__(bad_node, column, source_code_line, description)


class TableRangeError(SemanticError):
    def __init__(self, bad_node: LitInt, column: int, error_type: str, source_code_line: Optional[str] = None, description: Optional[str] = None):
        super().__init__(bad_node, column, source_code_line, description)
        
        # Not technically necessary, but forces the type to cast it to "LitInt"
        self.bad_node = bad_node

        self.error_type = error_type

    def __str__(self) -> str:
        result = ""

        result += f"{line_column_str(self.bad_node.lineno, self.column)}"

        if self.source_code_line is not None:
            result += f"  {self.bad_node.lineno} | {self.source_code_line} \n"
            result += f"  {arrow_line(self.bad_node.lineno, self.column)}"
            
        result += f"Erreur sémantique: {self.error_type}"

        if self.description is not None:
            result += f"\n -> {self.description}"

        return result

class TableRangeInvalidEndError(TableRangeError):
    def __init__(self, bad_node: LitInt, column: int, source_code_line: Optional[str] = None, description: Optional[str] = None):
        super().__init__(bad_node, column, f"Indice de fin '{bad_node.value}' incorrect", source_code_line, description)