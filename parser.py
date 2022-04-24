from __future__ import annotations

from ast_nodes import *

import ply.yacc as yacc
from errors import e_SyntaxError
from lexer import MyLexer


class MyParser:
    tokens = MyLexer.tokens

    def __init__(self, lexer: MyLexer, debug=False) -> None:
        self.lexer = lexer
        self.parser = yacc.yacc(module=self)
        self.debug = debug

        self.source_code: str = ""
        self.source_code_lines: list[str] = []

        self.syntax_errors: list[e_SyntaxError] = []


    def parse(self, source_code: str) -> Program:
        self.source_code = source_code
        self.source_code_lines = source_code.split("\n")

        return self.parser.parse(source_code, debug=self.debug)

    def find_column(self, token):
        line_start = self.source_code.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1

    def add_error(self, error):
        self.syntax_errors.append(error)
        print(error)

    def p_program(self, p):
        '''program : variables_declaration_list'''
        p[0] = Program(p[1], [])


    def p_variables_declaration_list(self, p):
        '''variables_declaration_list : VARIABLES opt_colon NEWLINE
                                      | variables_declaration_list variable_declaration_line
                                      | variables_declaration_list NEWLINE'''
        if len(p) == 4:
            p[0] = []
            return

        p[0] = p[1]
        if p[2] != "\n":
            p[0].append(p[2])

    def p_variables_declaration_list_error(self, p):
        '''variables_declaration_list : VARIABLES ':' error NEWLINE
                                      | VARIABLES error NEWLINE
        '''

        bad_token = list(p)[-2]
        bad_token_column = self.find_column(bad_token)
        source_line = self.source_code_lines[bad_token.lineno-1]

        possible_expected = [
            "New line",
            "':' or new line"
        ]

        expected = possible_expected[5 - len(p)]

        e = e_SyntaxError(bad_token, bad_token_column, source_code_line=source_line, expected=expected)
        self.add_error(e)

        p[0] = []


    def p_var_section_statement(self, p):
        '''variable_declaration_line : id_list ':' complex_type NEWLINE'''
        p[0] = VariableDeclarationLine(p[1], p[3])


    def p_var_section_statement_error(self, p):
        '''variable_declaration_line : id_list ':' complex_type error NEWLINE
                                     | id_list ':' error NEWLINE
                                     | id_list error NEWLINE
                                     | error NEWLINE
        '''

        bad_token = list(p)[-2]
        bad_token_column = self.find_column(bad_token)
        source_line = self.source_code_lines[bad_token.lineno-1]

        possible_expected = [
            "New line",
            "Variable type (ie. 'entier' ou 'tab[1...5] de entier' ou 'ptr vers entier'",
            "':'",
            "New variable declarations (ie. var1, var2: entier)"
            ]
        
        expected = possible_expected[6 - len(p)]

        e = e_SyntaxError(bad_token, bad_token_column, source_code_line=source_line, expected=expected)

        self.add_error(e)

    # A list of IDs seperated by an optional coma
    def p_id_list(self, p):
        '''id_list : ID opt_coma
                   | id_list ID opt_coma
        '''

        if type(p[1]) is list:
            p[0] = p[1] + [p[2]]
            return

        p[0] = [p[1]]


    def p_complex_type(self, p):
        '''complex_type : type_modifier_list basetype
                        | basetype'''

        if len(p) == 2:
            p[0] = ComplexType(p[1], [])
            return

        p[0] = ComplexType(p[2], p[1])

    
    def p_complex_type_error(self, p):
        '''complex_type : error basetype
        '''

        bad_token = list(p)[-2]
        bad_token_column = self.find_column(bad_token)
        source_line = self.source_code_lines[bad_token.lineno-1]

        expected = "Variable type (ie. 'entier' ou 'tab[1...5] de ' ou 'ptr vers entier')"

        e = e_SyntaxError(bad_token, bad_token_column, source_code_line=source_line, expected=expected)

        self.add_error(e)


    def p_basetype(self, p):
        '''basetype : ID
                    | REEL
                    | ENTIER'''

        p[0] = p[1]


    def p_type_modifier_list(self, p):
        '''type_modifier_list : type_modifier
                              | type_modifier_list type_modifier'''
        
        if len(p) == 2:
            p[0] = [p[1]]
            return

        p[0] = p[1]
        p[0].append(p[2])


    def p_type_modifier(self, p):
        '''type_modifier : pointeur_vers
                          | table_parameters'''
        p[0] = p[1]


    def p_ptr(self, p):
        '''ptr : POINTEUR
               | PTR
        '''


    def p_pointeur_vers(self, p):
        '''pointeur_vers : ptr opt_vers'''
        p[0] = PtrTypeModifier()

    def p_pointeur_vers_error(self, p):
        '''pointeur_vers : ptr error'''

        bad_token = p[2]
        bad_token_column = self.find_column(bad_token)
        source_line = self.source_code_lines[bad_token.lineno-1]

        expected = "'vers' ou type du pointeur"

        e = e_SyntaxError(bad_token, bad_token_column, source_code_line=source_line, expected=expected)

        self.add_error(e)


    def p_table_parameters(self, p):
        '''table_parameters : tab '[' lit_int POINTS lit_int ']' opt_de'''

        p[0] = TableTypeModifier(p[3].value, p[5].value)

    def p_table_parameters_error(self, p):
        '''table_parameters : tab '[' lit_int POINTS lit_int ']' error
                            | tab '[' lit_int POINTS lit_int error
                            | tab '[' lit_int POINTS error
                            | tab '[' lit_int error
                            | tab '[' error
                            | tab error
        '''

        bad_token = list(p)[-1]
        bad_token_column = self.find_column(bad_token)
        source_line = self.source_code_lines[bad_token.lineno-1]

        possible_expected = [
            "'de' ou type du tableau",
            "']'",
            "End of table range (positive integer)",
            "Range seperator ('...')",
            "Start of table range (positive integer)",
            "'['"
            ]
        
        expected = possible_expected[8 - len(p)]

        e = e_SyntaxError(bad_token, bad_token_column, source_code_line=source_line, expected=expected)

        self.add_error(e)

    def p_tab(self, p):
        '''tab : TABLEAU
            | TAB'''
        pass

    ### Optionals
    def p_opt_de(self, p):
        '''opt_de : DE
                  | empty'''

    def p_opt_vers(self, p):
        '''opt_vers : VERS
                    | empty'''

    def p_opt_colon(self, p):
        ''' opt_colon : ':'
                      | empty'''
        p[0] = "opt_colon"

    def p_opt_coma(self, p):
        ''' opt_coma : ','
                     | empty'''
        p[0] = "opt_coma"
    ### ### ###

    ### Basics
    def p_lit_int(self, p):
        '''lit_int : LIT_INT'''
        p[0] = LitInt(p[1])

    def p_lit_float(self, p):
        '''lit_float : LIT_FLOAT'''
        p[0] = LitFloat(p[1])

    def p_empty(self, p):
        '''empty : '''
        pass
    ### ### ###


    def p_error(self, token):
        print(token)
        pass