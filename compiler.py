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
        program = self.parser.parse(source_code)
        if self.parser.syntax_errors:
            return "", self.parser.syntax_errors

        print(f"name: {program.main_algorithm.name}")
        print(f" variables: ")
        for v in program.main_algorithm.variable_declarations:
            var_type = v.type
            for name in v.names:
                print(f"  {name}: {var_type}")
        print(f" instructions:")
        for s in program.main_algorithm.statements:
            print(f"  {s}")

        print("sub algos: ")
        for s_algo in program.sub_algorithms_list:
            print(f"  {s_algo.name}")
            for v in s_algo.variable_declarations:
                var_type = v.type
                for name in v.names:
                    print(f"    {name}: {var_type}")

        semantics = MySemantics()
        success, errors = semantics.verify_semantics(program)

        if not success:
            print("error")
            return "", errors

        return "", []


if __name__ == "__main__":
    with open("program.NF04") as fp:
        source_code = fp.read()

    compiler = MyCompiler(debug = True)


    result, errors = compiler.compile(source_code)

    for error in errors:
        print(error)
        print()
