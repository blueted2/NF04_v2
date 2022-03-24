from collections import namedtuple
from logging.config import IDENTIFIER
import ply.yacc as yacc
from lexer import tokens


VarDefs = namedtuple("Variables", ["var_line_defs"])
def p_var_defs(p):
    ''' var_defs : VARIABLES ":" NEWLINE
                  | var_defs var_line_def'''
    if len(p) == 4:
        p[0] = VarDefs([])
    elif p[2]:
        p[0] = VarDefs(p[1].var_line_defs + [p[2]])
    else:
        p[0] = VarDefs(p[1].var_line_defs)


VarLineDef = namedtuple("VarLineDef", ["vars", "type"])
def p_var_line_def(p):
    '''var_line_def : id_list ':' type NEWLINE
                    | NEWLINE'''
    if len(p) == 5:
        p[0] = VarLineDef(p[1], p[3])
    else:
        p[0] = None

Type = namedtuple("Type", ["type", "is_pointer"])
def p_type(p):
    '''type : ID
            | ptr_vers type'''
    if len(p) == 3:
        p[0] = Type(p[2], True)
    else:
        p[0] = Type(p[1], False)

# A list of IDs seperated by an optional coma
def p_id_list(p):
    '''id_list : ID opt_coma
               | id_list ID opt_coma
               '''
    if isinstance(p[1], str):
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_ptr_vers(p):
    '''ptr_vers : POINTEUR
                | POINTEUR VERS'''

# An optional colon
def p_opt_colon(p):
    ''' opt_colon : ':'
                  | empty'''
    p[0] = p[1]


# An optional coma
def p_opt_coma(p):
    ''' opt_coma : ','
                  | empty'''
    p[0] = p[1]

def p_empty(p):
    '''empty : '''
    pass

parser = yacc.yacc()
