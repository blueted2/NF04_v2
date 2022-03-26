from __future__ import annotations

from dataclasses import dataclass
import ply.yacc as yacc
from lexer import tokens

### TYPES
@dataclass
class p_VariablesSection:
    var_lines: list[p_VarSectionStatement]
@dataclass
class p_VarSectionStatement:
    id_list: p_IDList
    type: p_Type
@dataclass
class p_TableType:
    type: p_Type
    start: p_LitInt
    end: p_LitInt

@dataclass
class p_PtrType:
    type: p_Type

@dataclass
class p_LitInt:
    value: int

@dataclass
class p_LitFloat:
    value: float

@dataclass
class p_ID:
    value: str

@dataclass
class p_IDList:
    id_list: list[p_ID]

@dataclass
class p_Program:
    variables_section: p_VariablesSection



p_Type = p_ID | p_TableType | p_PtrType

### Entry Point
def p_program(p):
    '''program : variables_section'''
    p[0] = p_Program(p[1])


### Type nodes
def p_type(p):
    '''type : id
            | ptr_type
            | table_type'''

    p[0] = p[1]


def p_ptr_type(p):
    '''ptr_type : POINTEUR type
                | POINTEUR VERS type
                | PTR type
                | PTR VERS type'''
    
    p[0] =  p_PtrType(p[len(p)-1])

def p_table_type(p):
    '''table_type : TABLEAU '[' lit_int POINTS lit_int ']' opt_de type
                  | TAB '[' lit_int POINTS lit_int ']' opt_de type
    '''

    p[0] = p_TableType(p[8], p[3], p[5])
### ### ###


### Optionals
def p_opt_de(p):
    '''opt_de : DE
              | empty'''

def p_opt_colon(p):
    ''' opt_colon : ':'
                  | empty'''
    p[0] = "opt_colon"

def p_opt_coma(p):
    ''' opt_coma : ','
                  | empty'''
    p[0] = "opt_coma"
### ### ###

### Basics
# Wrap the ID string in class. 
def p_id(p):
    '''id : ID'''
    p[0] = p_ID(p[1])

def p_lit_int(p):
    '''lit_int : LIT_INT'''
    p[0] = p_LitInt(p[1])

def p_lit_float(p):
    '''lit_float : LIT_FLOAT'''
    p[0] = p_LitFloat(p[1])

def p_empty(p):
    '''empty : '''
    pass
### ### ###


### Other
# A list of IDs seperated by an optional coma
def p_id_list(p):
    '''id_list : id opt_coma
               | id_list id opt_coma
               '''
    if isinstance(p[1], p_ID):
        p[0] = p_IDList([])
        new_id = p[1]
    else:
        p[0] = p[1]
        new_id = p[2]

    p[0].id_list.append(new_id)

### ### ###


### Variable declaration
def p_variables_section(p):
    ''' variables_section : VARIABLES opt_colon NEWLINE
                          | variables_section var_section_statement'''

    # First time 
    if len(p) == 4:
        p[0] = p_VariablesSection([])
        return
    
    p[0] = p[1]
    p[0].var_lines.append(p[2])


def p_var_section_statement(p):
    '''var_section_statement : id_list ':' type NEWLINE'''
    p[0] = p_VarSectionStatement(p[1], p[3])

### ### ###



parser = yacc.yacc()
