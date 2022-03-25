import ply.yacc as yacc
from lexer import tokens


def p_var_decls(p):
    ''' var_decls : VARIABLES opt_colon NEWLINE
                  | var_decls var_line_decl
                  | empty'''

    if len(p) == 2 or len(p) == 4: 
        p[0] = ("var_decls", [])
    elif len(p) == 3:
        lines = []
        if p[1]:
            lines = p[1][1]
        if p[2]:
            lines += [p[2]]

        p[0] = ("var_decls", lines)


def p_var_line_decl(p):
    '''var_line_decl : id_list ':' type NEWLINE
                    | NEWLINE'''
    if len(p) == 5:
        p[0] = ("var_line_decl", p[1], p[3])
    else:
        p[0] = ("var_line_decl")


def p_table_type(p):
    '''table_type : TABLEAU '[' lit_num POINTS lit_num ']' opt_de type
                  | TAB '[' lit_num POINTS lit_num ']' opt_de type
    '''

    p[0] = ("table_type", p[8], p[3], p[5])

def p_opt_de(p):
    '''opt_de : DE
              | empty'''

def p_type(p):
    '''type : id
            | ptr_type
            | table_type'''

    if p[1][0] == 'id':
        p[0] = ("type_id", p[1][1])
    else:
        p[0] = p[1]


# A list of IDs seperated by an optional coma
def p_id_list(p):
    '''id_list : id opt_coma
               | id_list id opt_coma
               '''
    if p[1][0] == "id":
        p[0] = ("id_list", [p[1][1]])
    else:
        p[0] = ("id_list", p[1][1] + [p[2][1]])

def p_ptr_type(p):
    '''ptr_type : POINTEUR type
                | POINTEUR VERS type
                | PTR type
                | PTR VERS type'''
    
    p[0] = ("ptr_type", p[len(p)-1])

# An optional colon
def p_opt_colon(p):
    ''' opt_colon : ':'
                  | empty'''
    p[0] = ("opt_colon", p[1])

def p_lit_num(p):
    '''lit_num : LIT_NUM'''

    p[0] = ('lit_num', p[1])


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
