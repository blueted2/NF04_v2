

from parser import build_parser, Program, TableTypeModifier


def check(program_tree: Program):
    variables = dict()
    basetypes = ['reel', 'entier']

    for var_declaration_line in program_tree.variable_declarations:
        var_type = var_declaration_line.type
        if var_type.base_type not in basetypes:
            raise Exception()

        for modifier in var_type.modifiers:
            if isinstance(modifier, TableTypeModifier):
                if modifier.start not in [0, 1]:
                    raise Exception()
                if modifier.start >= modifier.end:
                    raise Exception()

        for var_name in var_declaration_line.names:
            if var_name in variables.keys():
                raise Exception()

            variables[var_name] = var_declaration_line.type

        var_declaration_line.names

    print(variables)

with open("program.NF04", 'r') as fp:
    data = fp.read()    

parser = build_parser()

check(parser.parse(data, debug=False, tracking=True))