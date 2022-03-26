from parser import p_ID, p_Program, p_PtrType, p_TableType, p_VariablesSection, p_VarSectionStatement, parser
from lexer import lexer

def compile(input_file, output_file):
    with open(input_file, 'r') as fp:
        text = fp.read()

    tree = parser.parse(text, debug=True)

    result = try_compile(tree)
    
    with open(output_file, 'w') as fp:
        fp.write(result)

def try_compile(node):
    type = node.__class__.__name__[2:]

    func = globals().get(f"c_{type}", None)
    if func:
        return func(node)
    else:
        raise RuntimeError(f"Missing function for {type} node.")

def c_VariablesSection(variablesSection: p_VariablesSection):
    var_line_decls = variablesSection.var_lines
    result = ""
    for var_line_decl in var_line_decls:
        result += try_compile(var_line_decl) + "\n"

    return result


def add_inner_par(str):
    return str.format("({})")

def c_Program(program: p_Program):
    return try_compile(program.variables_section)

def c_VarSectionStatement(var_line_decl: p_VarSectionStatement):

    type = var_line_decl.type
    id_list = var_line_decl.id_list

    id_format = "{}"
    last_modif = None

    while not isinstance(type, p_ID):
        if isinstance(type, p_TableType):
            start = int(type.start.value)
            end = int(type.end.value)
            type = type.type

            if last_modif == "ptr":
                id_format = add_inner_par(id_format)
            last_modif = "table"

            size = str(end - start)
            
            id_format = id_format.format(f"{{}}[{size}]")

        elif isinstance(type, p_PtrType):
            type = type.type

            if last_modif == "table":
                id_format = add_inner_par(id_format)
            last_modif = "ptr"

            id_format = id_format.format(f"*{{}}")

        else:
            raise Exception("")

    ids_with_modifs = ", ".join([id_format.format(id.value) for id in id_list.id_list])

    return f"{type.value} {ids_with_modifs};"

def c_id_list(ids):
    return ", ".join(ids)

def c_type(type):
    return try_compile(type)

def c_table_type(type, start, end):
    return f"{try_compile(type)}[{try_compile(start)}]"

def c_type_id(id):
    return f"{id}"

def c_ptr_type(type):
    return f"{try_compile(type)}*"

def c_lit_num(lit_num):
    return lit_num[1]

def c_id(id):
    return f"{id}"

compile("program.NF04", "out.c")