from typing import Optional
from lexer import MyLexer

class e_SyntaxError:

    def __init__(self, token, column, expected: Optional[str] = None, source_code_line: Optional[str] = None, error_type: Optional[str] = None, details: Optional[str] = None):
        self.token = token
        self.column = column
        self.expected = expected
        self.source_code_line = source_code_line
        self.error_type = error_type
        self.details = details

    def line_column_str(self):
        return f"Ligne {self.token.lineno}, colonne {self.column} \n"

    def arrow_line(self):
        num_len = len(str(self.token.lineno))
        return " " * num_len + " | " + " " * (self.column - 1) + "^ \n"

    def __str__(self):


        result = ""
        result += f"{self.line_column_str()}"

        if self.source_code_line is not None:
            result += f"  {self.token.lineno} | {self.source_code_line} \n"
            result += f"  {self.arrow_line()}"

        opt_kw_str         = "mot clé " if self.token.type in MyLexer.reserved else ""
        type_str           = f"'{self.token.type}' "
        opt_value_str      = f"({repr(self.token.value)}) " if str(self.token.type) != str(self.token.value) else ""
        opt_error_type_str = f" -> {self.error_type} " if self.error_type is not None else ""

        result += f"Erreur de syntaxe: {opt_kw_str}{type_str}{opt_value_str}inattendu{opt_error_type_str}\n"
        
        if self.details is not None:
            result += f"{self.details}\n"

        if self.expected is not None:
            result += f" -> Attendu: {self.expected}"

        return result