from parser import parser

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

def c_var_defs(var_line_defs):
    result = ""
    for var_line_def in var_line_defs:
        result += try_compile(var_line_def) + "\n"

    return result
    

def c_var_line_def(id_list, type):
    return f"{try_compile(type)} {try_compile(id_list)};"

def c_id_list(ids):
    return ", ".join(ids)

def c_type(id):
    return try_compile(id)

def c_ptr_type(type):
    return f"{try_compile(type)}*"

def c_id(id):
    return f"{id}"

compile("program.NF04", "out.c")