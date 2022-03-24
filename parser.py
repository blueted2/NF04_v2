from collections import namedtuple
import ply.yacc as yacc
from lexer import tokens


def p_var_defs(p):
    ''' var_defs : VARIABLES ":" NEWLINE
                  | var_defs var_line_def'''
    if len(p) == 4:
        p[0] = ("var_defs", [])
    elif p[2]:
        p[0] = ("var_defs", p[1][1] + [p[2]])
    else:
        p[0] = ("var_defs", p[1][1])


def p_var_line_def(p):
    '''var_line_def : id_list ':' type NEWLINE
                    | NEWLINE'''
    if len(p) == 5:
        p[0] = ("var_line_def", p[1], p[3])
    else:
        p[0] = ("var_line_def")

def p_type(p):
    '''type : id
            | ptr_vers type'''
    if len(p) == 3:
        p[0] = ("ptr_type", p[2])
    else:
        p[0] = ("type", p[1])
        

# A list of IDs seperated by an optional coma
def p_id_list(p):
    '''id_list : id opt_coma
               | id_list id opt_coma
               '''
    if p[1][0] == "id":
        p[0] = ("id_list", [p[1][1]])
    else:
        p[0] = ("id_list", p[1][1] + [p[2][1]])

def p_ptr_vers(p):
    '''ptr_vers : POINTEUR
                | POINTEUR VERS'''

# An optional colon
def p_opt_colon(p):
    ''' opt_colon : ':'
                  | empty'''
    p[0] = ("opt_colon", p[1])


def p_id(p):
    '''id : ID'''
    p[0] = ('id', p[1])

# An optional coma
def p_opt_coma(p):
    ''' opt_coma : ','
                  | empty'''
    p[0] = ("opt_coma", p[1])

def p_empty(p):
    '''empty : '''
    pass

parser = yacc.yacc()
