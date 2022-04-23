from typing import Optional

class e_SyntaxError:

    def __init__(self, token, column, expected: Optional[str] = None, source_code_line: Optional[str] = None):
        self.token = token
        self.column = column
        self.expected = expected
        self.source_code_line = source_code_line

    def line_column_str(self):
        return f"Line {self.token.lineno}, column {self.column} \n"

    def arrow_line(self):
        return " " * (self.column - 1) + "^ \n"

    def __str__(self):

        result = ""
        result += f"  {self.line_column_str()}"

        if self.source_code_line is not None:
            result += f"    {self.source_code_line} \n"
            result += f"    {self.arrow_line()}"
        
        if str(self.token.type) == str(self.token.value):
            result += f"SyntaxError: Unexpected '{self.token.type}' \n"
        else:
            result += f"SyntaxError: Unexpected '{self.token.type}' ('{self.token.value}') \n"
        
        if self.expected is not None:
            result += f" -> Expected: {self.expected}"

        return result