import sys
from typing import Optional, Tuple
from lexer import MyLexer
from parser import MyParser
from semantics import MySemantics

class MyCompiler:
    def __init__(self, lexer: Optional[MyLexer] = None, parser: Optional[MyParser] = None, debug = False) -> None:
        if parser is None:
            if lexer is None: lexer = MyLexer()
            parser = MyParser(lexer, debug=debug)

        self.parser = parser

    def compile(self, source_code) -> Tuple[str, list]:
        # Add an extra line return if there isn't one at the end
        if source_code[-1] != "\n":
            source_code += "\n"

        program = self.parser.parse(source_code)
        if self.parser.syntax_errors:
            return "", self.parser.syntax_errors

        print(program)

        semantics = MySemantics(self.parser)
        success, errors = semantics.verify_semantics(program)

        if not success:
            print("error")
            return "", errors

        return "", []


if __name__ == "__main__":
    with open("program.NF04", encoding='utf-8') as fp:
        source_code = fp.read()

    compiler = MyCompiler(debug = True)


    result, errors = compiler.compile(source_code)

    for error in errors:
        print(error)
        print()
