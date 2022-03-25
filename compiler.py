from parser import parser
from lexer import lexer

def compile(input_file, output_file):
    with open(input_file, 'r') as fp:
        text = fp.read()

    tree = parser.parse(text, debug=False)
    result = try_compile(tree)
    
    with open(output_file, 'w') as fp:
        fp.write(result)

def try_compile(node):
    type = node[0]

    func = globals().get(f"c_{type}", None)
    if func:
        return func(*node[1:])
    else:
        raise RuntimeError(f"Missing function for {type} node.")

def c_var_decls(var_line_decls):
    result = ""
    for var_line_decl in var_line_decls:
        result += try_compile(var_line_decl) + "\n"

    return result
    

def add_inner_par(str):
    return str.format("({})")

def c_var_line_decl(id_list, type):

    id_format = "{}"
    last_modif = None

    while type[0] != "type_id":
        if type[0] == "table_type":
            _, type, start, end = type
            if last_modif == "ptr":
                id_format = add_inner_par(id_format)

            last_modif = "table"

            size = int(end[1][1]) - int(start[1][1])
            size = str(size)
            
            id_format = id_format.format(f"{{}}[{size}]")

        elif type[0] == "ptr_type":
            _, type = type
            if last_modif == "table":
                id_format = add_inner_par(id_format)

            last_modif = "ptr"
            id_format = id_format.format(f"*{{}}")

        else:
            raise Exception("")

    ids_with_modifs = ", ".join([id_format.format(id) for id in id_list[1]])

    return f"{type[1]} {ids_with_modifs};"

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