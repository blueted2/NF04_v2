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
        if self.debug:
            print(error)

    def add_syntax_error(self, bad_token, expected: Optional[str] = None, error_type: Optional[str] = None, details: Optional[str] = None):
        col = self.find_column(bad_token)
        line = self.source_code_lines[bad_token.lineno-1]
        
        self.add_error(e_SyntaxError(bad_token, col, expected, line, error_type, details))


    def p_program_def(self, p):
        '''program_def : main_algo_definition opt_sub_algo_defs_list'''
        p[0] = Program(p[1], p[2], [])

        print(list(p))


    def p_opt_sub_algo_defs_list(self, p):
        '''opt_sub_algo_defs_list : sub_algo_defs_list
                                  | empty'''

        p[0] = p[1] if p[1] is not None else []

    def p_sub_algo_defs_list(self, p):
        '''sub_algo_defs_list : sub_algo_definition'''
        p[0] = [p[1]]
    
    def p_sub_algo_defs_list_append(self, p):
        '''sub_algo_defs_list : sub_algo_defs_list sub_algo_definition'''
        p[0] = p[1] + [p[2]]


    def p_sub_algo_definition(self, p):
        '''sub_algo_definition : SA ID colon_newline var_declaration_section statements_section'''
        p[0] = SubAlgorithm(p[2], p[4], [], [], [])

    def p_main_algo_definition(self, p):
        '''main_algo_definition : algo_header var_declaration_section statements_section'''
        p[0] = MainAlgorithm(p[1], p[2], p[3])


    def p_var_declaration_section(self, p):
        '''var_declaration_section : variables_header opt_var_declaration_list'''
        p[0] = p[2]
    
    def p_var_declaration_section_error(self, p):
        '''var_declaration_section : error var_declaration_section
                                   | error
        '''
        p[0] = p[2] if len(p) == 3 else []
        self.add_syntax_error(p[1], "Variable declaration section")


    def p_opt_var_declaration_list(self, p):
        '''opt_var_declaration_list : var_declaration_list
                                    | empty
        '''
        p[0] = p[1] if p[1] is not None else []
    
    def p_var_declaration_list(self, p):
        '''var_declaration_list : var_declaration_line'''
        p[0] = [p[1]]
    
    def p_var_declaration_list_append(self, p):
        '''var_declaration_list : var_declaration_list var_declaration_line'''
        p[0] = p[1] + [p[2]]


    def p_var_declaration_line(self, p):
        '''var_declaration_line : id_list colon complex_type newline'''
        p[0] = VariableDeclarationLine(p[1], p[3])


    def p_complex_type(self, p):
        '''complex_type : basetype
                        | table_type
                        | pointer_type
        '''
        p[0] = p[1]

    def p_complex_type_error(self, p):
        '''complex_type : error'''
        self.add_syntax_error(p[1], expected="Complex type")

    def p_basetype(self, p):
        '''basetype : ID
                    | REEL
                    | ENTIER'''
        p[0] = p[1]

    def p_pointer_type(self, p):
        '''pointer_type : ptr complex_type'''
        p[0] = PtrType(p[2])


    def p_table_type(self, p):
        '''table_type : tab '[' lit_int POINTS lit_int ']' opt_de complex_type  '''
        p[0] = TableType(p[3], p[5], p[8])

    def p_table_type_error_closing(self, p):
        '''table_type : tab '[' lit_int POINTS lit_int error'''
        self.add_syntax_error(p[6], "Closing ']'")

    def p_table_type_error_end(self, p):
        '''table_type : tab '[' lit_int POINTS error'''
        self.add_syntax_error(p[5], "End of range")

    def p_table_type_error_points(self, p):
        '''table_type : tab '[' lit_int error'''
        self.add_syntax_error(p[4], "Range seperator")

    def p_table_type_error_start(self, p):
        '''table_type : tab '[' error'''
        self.add_syntax_error(p[3], "Start of range")

    def p_table_type_error_opening(self, p):
        '''table_type : tab error'''
        self.add_syntax_error(p[2], "Opening '['")


    def p_statements_section(self, p):
        '''statements_section : instructions_header opt_statements_list'''
        p[0] = p[2]

    def p_opt_statements_list(self, p):
        '''opt_statements_list : statements_list
                               | empty'''
        p[0] = p[1] if p[1] is not None else []

    def p_statements_list(self, p):
        '''statements_list : statement'''
        p[0] = [p[1]]

    def p_statements_list_append(self, p):
        '''statements_list : statements_list statement'''
        p[0] = p[1] + [p[2]]
    
    def p_statements_list_error(self, p):
        '''statements_list : error'''
        
        bad_token = p[1]
        expected = "List of statements"

        self.add_syntax_error(bad_token, expected)


    def p_statement(self, p):
        '''statement : DUMMY newline'''
        p[0] = p[1]



    # A list of IDs seperated by an optional coma
    def p_id_list(self, p):
        '''id_list : ID opt_coma
                   | id_list ID opt_coma
        '''

        if type(p[1]) is list:
            p[0] = p[1] + [p[2]]
            return

        p[0] = [p[1]]
    

    def p_ptr(self, p):
        '''ptr : POINTEUR opt_vers
               | PTR opt_vers
        '''

    def p_tab(self, p):
        '''tab : TABLEAU
               | TAB'''
        pass


    ### Optional keywords
    def p_opt_de(self, p):
        '''opt_de : DE
                  | empty'''

    def p_opt_vers(self, p):
        '''opt_vers : VERS
                    | empty'''

    def p_opt_coma(self, p):
        ''' opt_coma : ','
                     | empty'''
        p[0] = "opt_coma"
    ### ### ###

    def p_colon_newline(self, p):
        '''colon_newline : colon newline'''

    ### Basics
    def p_lit_int(self, p):
        '''lit_int : LIT_INT'''
        p[0] = p[1]
    
    def p_lit_float(self, p):
        '''lit_float : LIT_FLOAT'''
        p[0] = p[1]

    def p_empty(self, p):
        '''empty : '''
        pass

    def p_newline(self, p):
        '''newline : NEWLINE'''
        p[0] = "\n"
    
    def p_newline_error(self, p):
        '''newline : error NEWLINE'''
        
        bad_token = p[1]
        expected = "New line"

        self.add_syntax_error(bad_token, expected)
    
    def p_colon(self, p):
        '''colon : ':' '''
    
    def p_colon_error(self, p):
        '''colon : error ':' '''
        self.add_syntax_error(p[1], expected="':'")

    def p_square_brackets(self, p):
        '''l_square : '[' 
           r_square : ']'
        '''

    def p_r_square_error(self, p):
        '''r_square : error opt_de complex_type'''
        self.add_syntax_error(p[1], expected="']'")

    ### Section Headers
    def p_algo_header(self, p):
        '''algo_header : ALGO ID newline '''
        p[0] = p[2]
    
    def p_algo_header_name_error(self, p):
        '''algo_header : ALGO error'''
        self.add_syntax_error(p[2], "Algo name")

    def p_basic_headers(self, p):
        '''variables_header    : VARIABLES colon_newline
           instructions_header : INSTRUCTIONS colon_newline
        '''

    def p_error(self, token):
        print("parse error")
        print(token)
        pass