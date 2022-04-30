from __future__ import annotations
from typing import Optional

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
        '''program_def : main_algo_definition opt_sub_algo_defs_list EOF'''
        p[0] = Program(p[1], p[2])

    
    def p_program_error(self, p):
        '''program_def : main_algo_definition sub_algo_defs_list error'''
        self.add_syntax_error(p[3], "Sous-algo or EOF")


    def p_main_algo_definition(self, p):
        '''main_algo_definition : ALGORITHME id newline opt_type_defs_section opt_variables_section opt_statements_section FINALGO newline'''
        p[0] = MainAlgorithm(p[2], [], p[5], p[6])


    def p_main_algo_definition_error_finalgo(self, p):
        '''main_algo_definition : ALGORITHME id newline opt_type_defs_section opt_variables_section statements_section error'''
        self.add_syntax_error(p[7], "Instruction or 'FinAlgo'")

    def p_main_algo_definition_error_statements(self, p):
        '''main_algo_definition : ALGORITHME id newline opt_type_defs_section variables_section error'''
        self.add_syntax_error(p[6], "Variable declaration or instructions section or 'FinAlgo'")

    def p_main_algo_definition_error_variables(self, p):
        '''main_algo_definition : ALGORITHME id newline type_defs_section error'''
        self.add_syntax_error(p[5], "Variables section or instructions section or 'FinAlgo'")

    def p_main_algo_definition_error_typedef(self, p):
        '''main_algo_definition : ALGORITHME id newline error'''
        self.add_syntax_error(p[4], "Type definitions section or variables section or instructions section or 'FinAlgo'")
    
    def p_main_algo_definition_error_name(self, p):  
        '''main_algo_definition : ALGORITHME error'''
        self.add_syntax_error(p[2], "Algorithm Name")


    def p_opt_type_defs_section(self, p):
        '''opt_type_defs_section : type_defs_section
                                 | empty'''
        p[0] = p[1] if p[1] is not None else []

    def p_type_defs_section(self, p):
        '''type_defs_section : types_header'''
        p[0] = p[1]


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
        '''sub_algo_definition : sub_algo_header opt_inputs_section opt_outputs_section opt_variables_section opt_statements_section FINSA newline'''
        p[0] = SubAlgorithm(p[1], p[2], p[3], p[4], p[5])




    def p_opt_variables_section(self, p):
        '''opt_variables_section : variables_section
                                 | empty'''
        p[0] = p[1] if p[1] is not None else []

    def p_variables_section(self, p):
        '''variables_section : variables_header opt_var_declaration_list'''
        p[0] = p[2]


    def p_opt_inputs_section(self, p):
        '''opt_inputs_section : inputs_section
                              | empty'''

    def p_inputs_section(self, p):
        '''inputs_section : inputs_header opt_var_declaration_list'''


    def p_opt_outputs_section(self, p):
        '''opt_outputs_section : outputs_section
                               | empty'''

    def p_outputs_section(self, p):
        '''outputs_section : outputs_header opt_var_declaration_list'''


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
        '''basetype : id
                    | REEL
                    | ENTIER'''
        p[0] = p[1]

    def p_pointer_type(self, p):
        '''pointer_type : POINTEUR opt_sur complex_type'''
        p[0] = PtrType(p[3], p=p)


    def p_table_type(self, p):
        '''table_type : TABLEAU '[' lit_int POINTS lit_int ']' opt_de complex_type  '''
        p[0] = TableType(p[3], p[5], p[8])

    def p_table_type_error_closing(self, p):
        '''table_type : TABLEAU '[' lit_int POINTS lit_int error'''
        self.add_syntax_error(p[6], "Closing ']'")

    def p_table_type_error_end(self, p):
        '''table_type : TABLEAU '[' lit_int POINTS error'''
        self.add_syntax_error(p[5], "End of range")

    def p_table_type_error_points(self, p):
        '''table_type : TABLEAU '[' lit_int error'''
        self.add_syntax_error(p[4], "Range seperator")

    def p_table_type_error_start(self, p):
        '''table_type : TABLEAU '[' error'''
        self.add_syntax_error(p[3], "Start of range")

    def p_table_type_error_opening(self, p):
        '''table_type : TABLEAU error'''
        self.add_syntax_error(p[2], "Opening '['")


    def p_opt_statements_section(self, p):
        '''opt_statements_section : statements_section
                                  | empty'''
        p[0] = p[1] if p[1] is not None else []


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


    def p_statement(self, p):
        '''statement : assignment_statement
                     | expression_statement
                     | function_statement
                     | pour_statement'''
        p[0] = p[1]


    def p_assignment_statement(self, p):
        '''assignment_statement : unary_expression L_ARROW expression newline'''
        p[0] = AssignmentStatement(p[1], p[3], s=p[1])


    def p_expression_statement(self, p):
        '''expression_statement : expression newline'''
        p[0] = ExpressionStatement(p[1], s=p[1])

    
    def p_function_statement(self, p):
        '''function_statement : id '(' opt_expression_list '!' opt_id_list ')' newline'''
        p[0] = FunctionStatement(p[1], p[3], p[5], s=p[1])

    def p_function_statement_error(self, p):
        '''postfix_expression : id '(' opt_expression_list '!' opt_id_list error NEWLINE'''
        self.add_syntax_error(p[5], "Closing ')'")


    def p_pour_statement(self, p):
        '''pour_statement : POUR id ALLANT DE expression A expression newline opt_statements_list FINPOUR newline'''
        p[0] = PourStatement(p[2], p[5], p[7], p[9], p=p)

    def p_pour_statement_error_finpour(self, p):
        '''pour_statement : POUR id ALLANT DE expression A expression newline opt_statements_list error '''
        self.add_syntax_error(p[10], "FinPour")

    def p_pour_statement_error_end_expression(self, p):
        '''pour_statement : POUR id ALLANT DE expression A error'''
        self.add_syntax_error(p[7], "End expression")

    def p_pour_statement_error_a(self, p):
        '''pour_statement : POUR id ALLANT DE expression error'''
        self.add_syntax_error(p[6], "'a'")

    def p_pour_statement_error_start_expression(self, p):
        '''pour_statement : POUR id ALLANT DE error'''
        self.add_syntax_error(p[5], "Start expression")

    def p_pour_statement_error_de(self, p):
        '''pour_statement : POUR id ALLANT error'''
        self.add_syntax_error(p[4], "'de'")

    def p_pour_statement_error_allant(self, p):
        '''pour_statement : POUR id error'''
        self.add_syntax_error(p[3], "'allant'")

    def p_pour_statement_error_variale(self, p):
        '''pour_statement : POUR error'''
        self.add_syntax_error(p[2], "Loop variable")
        

    def p_primary_expression(self, p):
        '''primary_expression : id
                              | lit_int
                              | lit_float'''
        p[0] = p[1]


    def p_primary_expression_parens(self, p):
        '''primary_expression : '(' expression ')' '''
        p[0] = SubExpression(p[2], p=p)
        

    def p_primary_expression_parens_error_closing(self, p):
        '''primary_expression : '(' expression error'''
        self.add_syntax_error(p[3], "Closing ')'")

    def p_p_primary_expression_parens_error_expression(self, p):
        '''primary_expression : '(' error'''
        self.add_syntax_error(p[2], "Expression")


    def p_expression(self, p):
        '''expression                : logical_or_expression
           expression                : function_expression
           logical_or_expression     : logical_and_expression
           logical_and_expression    : equality_expression
           equality_expression       : relational_expression
           relational_expression     : additive_expression
           additive_expression       : multiplicative_expression
           multiplicative_expression : unary_expression
           unary_expression          : postfix_expression'''
        p[0] = p[1]


    def p_logical_or_expression(self, p):
        '''logical_or_expression  : logical_or_expression OU logical_and_expression'''
        p[0] = BinaryOr(p[1], p[3], s=p[1])

    def p_logical_and_expression(self, p):
        '''logical_and_expression : logical_and_expression ET equality_expression'''
        p[0] = BinaryAnd(p[1], p[3], s=p[1])
            

    def p_additive_expression_plus(self, p):
        '''additive_expression : additive_expression '+' multiplicative_expression'''
        p[0] = BinaryPlus(p[1], p[3], s=p[1])

    def p_additive_expression_minus(self, p):
        '''additive_expression : additive_expression '-' multiplicative_expression'''
        p[0] = BinaryMinus(p[1], p[3], s=p[1])


    def p_multiplicative_expression_times(self, p):
        '''multiplicative_expression : multiplicative_expression '*' unary_expression''' 
        p[0] = BinaryTimes(p[1], p[3], s=p[1])

    def p_multiplicative_expression_divide(self, p):
        '''multiplicative_expression : multiplicative_expression '/' unary_expression'''
        p[0] = BinaryDivide(p[1], p[3], s=p[1])

    def p_multiplicative_expression_modulo(self, p):
        '''multiplicative_expression : multiplicative_expression '%' unary_expression'''
        p[0] = BinaryModulo(p[1], p[3], s=p[1])


    def p_binary_expression_error(self, p):
        '''logical_or_expression     : logical_or_expression     OU  error
           logical_and_expression    : logical_and_expression    ET  error
           additive_expression       : additive_expression       '+' error
           additive_expression       : additive_expression       '-' error
           multiplicative_expression : multiplicative_expression '*' error
           multiplicative_expression : multiplicative_expression '/' error
           multiplicative_expression : multiplicative_expression '%' error'''
        self.add_syntax_error(p[3], "Expression")



    def p_unary_expression_plus(self, p):
        '''unary_expression : '+' unary_expression'''
        p[0] = UnaryPlus(p[2], p=p)

    def p_unary_expression_minus(self, p):
        '''unary_expression : '-' unary_expression'''
        p[0] = UnaryMinus(p[2], p=p)

    def p_unary_expression_pointer(self, p):
        '''unary_expression : '&' unary_expression'''
        p[0] = UnaryDereference(p[2], p=p)

    def p_unary_expression_dereference(self, p):
        '''unary_expression : '^' unary_expression'''
        p[0] = UnaryPointer(p[2], p=p)

    def p_unary_expression_not(self, p):
        '''unary_expression : NON unary_expression'''
        p[0] = UnaryNot(p[2], p=p)

    def p_unary_expression_error(self, p):
        '''unary_expression : '+' error
                            | '-' error
                            | '&' error
                            | '^' error
                            | NON error'''
        self.add_syntax_error(p[2], "Expression")


    def p_postfix_expression(self, p):
        '''postfix_expression : primary_expression'''
        p[0] = p[1]
        

    def p_postfix_expression_attribut(self, p):
        '''postfix_expression : postfix_expression '.' id '''
        p[0] = AttributExpression(p[1], p[3], s=p[1])

    def p_postfix_expression_attribut_error(self, p):
        '''postfix_expression : postfix_expression '.' error'''
        self.add_syntax_error(p[3], "Attribut")

    def p_postfix_expression_table(self, p):
        '''postfix_expression : postfix_expression '[' expression ']' '''
        p[0] = TableExpression(p[1], p[3], s=p[1])

    def p_postfix_expression_table_error_closing(self, p):
        '''postfix_expression : postfix_expression '[' expression error'''
        self.add_syntax_error(p[4], "Closing ']'")

    def p_postfix_expression_table_error_expression(self, p):
        '''postfix_expression : postfix_expression '[' error'''
        self.add_syntax_error(p[3], "Expression")



    def p_function_expression(self, p):
        '''function_expression : id '(' opt_expression_list ')' '''
        p[0] = FunctionExpression(p[1], p[3], s=p[1])

    def p_function_expression_error(self, p):
        '''function_expression : id '(' opt_expression_list error'''
        self.add_syntax_error(p[4], "Closing ')'")

    def p_opt_id_list(self, p):
        '''opt_id_list : id_list
                       | empty'''
        p[0] = p[1] if p[1] is not None else []

    # A list of IDs seperated by an optional coma
    def p_id_list(self, p):
        '''id_list : id'''
        p[0] = [p[1]]

    def p_id_list_append(self, p):
        '''id_list : id_list ',' id'''
        p[0] = p[1] + [p[3]]


    def p_opt_expression_list(self, p):
        '''opt_expression_list : expression_list
                               | empty'''
        p[0] = p[1] if p[1] is not None else []


    def p_expression_list(self, p):
        '''expression_list : expression'''
        p[0] = [p[1]]

    # def p_expression_list_error(self, p):
    #     '''expression_list : error'''
    #     self.add_syntax_error(p[1], "Expression")

    def p_expression_list_append(self, p):
        '''expression_list : expression_list ',' expression'''
        p[0] = p[1] + [p[3]]

    def p_expression_list_append_error(self, p):
        '''expression_list : expression_list ',' error'''
        self.add_syntax_error(p[3], "Expression")

    ### Optional keywords
    def p_opt_de(self, p):
        '''opt_de : DE
                  | empty'''

    def p_opt_sur(self, p):
        '''opt_sur : SUR
                   | empty'''
    ### ### ###

    ### Basics
    def p_lit_int(self, p):
        '''lit_int : LIT_INT'''
        p[0] = LitInt(p[1], lineno=p.lineno(1), lexpos=p.lexpos(1), p=p)
    
    def p_lit_float(self, p):
        '''lit_float : LIT_FLOAT'''
        p[0] = LitFloat(p[1], lineno=p.lineno(1), lexpos=p.lexpos(1), p=p)

    def p_empty(self, p):
        '''empty : '''
        pass

    def p_newline(self, p):
        '''newline : NEWLINE'''
        p[0] = "\n"
    
    
    def p_newline_error(self, p):
        '''newline : error'''
        self.add_syntax_error(p[1], "Newline")



    def p_colon(self, p):
        '''colon : ':' '''
    
    def p_colon_error(self, p):
        '''colon : error'''
        self.add_syntax_error(p[1], expected="':'")

    def p_id(self, p):
        '''id : ID'''
        p[0] = ID(p[1], p=p)


    ### Section Headers
    def p_algo_header(self, p):
        '''sub_algo_header : SA id newline
        '''
        p[0] = p[2]
    

    def p_sub_algo_header_name_error(self, p):
        '''sub_algo_header : SA error'''
        self.add_syntax_error(p[2], "Sub-algo name")


    def p_basic_headers(self, p):
        '''types_header        : TYPES colon newline
           variables_header    : VARIABLES colon newline
           instructions_header : INSTRUCTIONS colon newline
           inputs_header       : PE colon newline
           outputs_header      : PS colon newline
        '''
        p[0] = p[1]

    def p_error(self, token):
        if token is None:
            print("eof error") 

        print(f"parse error: {token}")