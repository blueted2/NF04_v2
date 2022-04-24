import sys
from typing import Optional, Tuple
from lexer import MyLexer
from parser import MyParser
from semantics import MySemantics

class MyCompiler:
    def __init__(self, lexer: Optional[MyLexer] = None, parser: Optional[MyParser] = None) -> None:
        if parser is None:
            if lexer is None: lexer = MyLexer()
            parser = MyParser(lexer)

        self.parser = parser

    def compile(self, source_code) -> Tuple[str, list]:
        program = self.parser.parse(source_code)
        if self.parser.syntax_errors:
            return "", self.parser.syntax_errors

        semantics = MySemantics()
        success, errors = semantics.verify_semantics(program)

        if not success:
            print("error")
            return "", errors

        return "", []


if __name__ == "__main__":
    with open(sys.argv[1]) as fp:
        source_code = fp.read()

    compiler = MyCompiler()

    result, errors = compiler.compile(source_code)

    # for error in errors:
    #     print(error, "\n")
