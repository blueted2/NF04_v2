from __future__ import annotations
from ast_nodes import ID, AssignmentStatement, AttributeExpression, BaseType, BinaryAnd, BinaryDivide, BinaryEq, BinaryGT, BinaryGTE, BinaryLT, BinaryLTE, BinaryMinus, BinaryModulo, BinaryOperation, BinaryOr, BinaryPlus, BinaryTimes, CustomTypeDefinition, FunctionExpression, FunctionStatement, LitBool, LitChar, SiStatement, TantQueStatement, UnaryDereference, UnaryMinus, UnaryNot, UnaryOperation, UnaryPlus, UnaryPointer, VariableType, Expression, LitFloat, LitInt, MainAlgorithm, PourStatement, PtrType, Statement, SubAlgorithm, SubExpression, TableExpression, TableType, VariableDeclaration

from typing import Any, Optional, Tuple
from ast_nodes import Program
from errors import AttributeRedeclarationError, CKeywordError, DifferentTypesComparisonError, IdRedefinitionError, IncompatibleAssignmentTypesError, IncompatibleInputTypeError, IncompatibleOutputTypeError, InvalidAttributError, InvalidBinaryOperationTermType, InvalidUnaryOperationExpressionTypeError, NonAssignableExpressionError, NonBooleanIfConditionError, NonBooleanUnaryNotError, NonBooleanWhileConditionError, NonCustomTypeAttributeAccessError, NonIntegerEndError, NonIntegerIndexError, NonIntegerIterationVariableError, NonIntegerStartError, NonPointerDereferenceError, NonTableElementAccessError, NonUniqueOutputFunctionExpressionError, SemanticError, SubAlgoRedefinitionError, TableAssignmentError, TableEndNotDefinedForVariableError, TableIndexWrongTypeError, TableRangeInvalidEndError, TypeDefinitionRecursionError, TypeRedefinitionError, UndeclaredVariableError, UndefinedFunctionError, UnknownBaseTypeError, UnmatchedNumberOfInputsError, UnmatchedNumberOfOutputsError, UnmatchedTableIndexesError, VariableRedeclarationError
from parser import MyParser
from program_variables import AlgorithmVariables, ProgramVariables


REEL_T = "réel"
ENTIER_T = "entier"
BOOLEEN_T = "booléen"
CARACTERE_T = "caractère"

class MySemantics:
    BUILTIN_TYPES = [REEL_T, ENTIER_T, BOOLEEN_T, CARACTERE_T]

    C_KEYWORDS = [ 
        "auto", "double", "int", "struct", "break", "else", "long", "switch", 
        "case", "enum", "register", "typedef", "char", "extern", "return", "union",
        "const", "float", "short", "unsigned", "continue", "for", "signed", "void",
        "default", "goto", "sizeof", "volatile",
        "do", "if", "static", "while"
    ]

    def __init__(self, parser: MyParser) -> None:
        self.parser = parser
        self.semantic_errors: list[SemanticError] = []
        self.custom_types: dict[str, CustomTypeDefinition] = {}
        
        self.sous_algos: dict[str, SubAlgorithm] = {}

        # A list of 'bad' / unknown variable basetypes. Used to prevent a bad type from generating multiple errors for multiple variables.
        self._bad_var_types: set[str] = set()

    def add_error(self, error: SemanticError):
        self.semantic_errors.append(error)


    def verify_program_and_get_variables_or_errors(self, program: Program) -> Tuple[ProgramVariables, None] | Tuple[None, list[SemanticError]]:
        self.verify_type_definitions(program.main_algorithm.type_definitions)
        self.verify_s_algo_names(program.sub_algorithms_list)
        main_algo_variables = self.verify_main_algo_and_get_variables(program.main_algorithm)
        s_algo_variables = {}
        
        for algo in program.sub_algorithms_list:
            s_algo_variables[algo.name.value] = self.verify_sub_algo_and_get_variables(algo)

        if len(self.semantic_errors) > 0:
            return None, self.semantic_errors

        sub_algos = {s.name.value: s for s in program.sub_algorithms_list}

        return ProgramVariables(main_algo_variables, s_algo_variables, sub_algos), None

    def verify_type_definitions(self, type_defs: list[CustomTypeDefinition]):

        # First identify the names of all custom types
        for t in type_defs:
            name = t.name

            if name.value in self.C_KEYWORDS:
                e = CKeywordError(name)
                self.add_error(e)
            elif name.value in self.custom_types:
                e = TypeRedefinitionError(self.custom_types[name.value].name, name)
                self.add_error(e)
            else:
                self.custom_types[name.value] = t

        # Next, check the attributes
        for t in type_defs:
            attributes = t.attributes
            attribute_declarations: dict[str, VariableDeclaration] = {}

            for attribute in attributes:
                attr_name = attribute.name
                attr_type = attribute.type

                if attr_name.value in self.C_KEYWORDS:
                    e = CKeywordError(attr_name)
                    self.add_error(e)
                elif attr_name.value in attribute_declarations:
                    e = AttributeRedeclarationError(attribute_declarations[attr_name.value].name, attr_name, t.name.value)
                    self.add_error(e)
                else:
                    attribute_declarations[attr_name.value] = attribute

                self.verify_var_type(attr_type)

        # Finally, test for recursion errors
        for t in type_defs:
            if self.type_contains_type(BaseType(t.name.value), BaseType(t.name.value)):
                e = TypeDefinitionRecursionError(t.name)
                self.add_error(e)

    def type_contains_type(self, type_to_check: VariableType, other_type: VariableType, visited_custom_types: Optional[set[str]] = None) -> bool:
        if isinstance(type_to_check, PtrType):
            return False

        if visited_custom_types == None:
            visited_custom_types = set()

        if isinstance(type_to_check, BaseType):
            if type_to_check.value in visited_custom_types:
                return True

            if type_to_check.value not in self.custom_types:
                return False

            visited_custom_types.add(type_to_check.value)
            
            type_def = self.custom_types[type_to_check.value]
            for attr in type_def.attributes:
                if self.type_contains_type(attr.type, other_type, visited_custom_types):
                    return True

            return False

        if isinstance(type_to_check, TableType):
            return self.type_contains_type(type_to_check.type, other_type, visited_custom_types)

        raise Exception("")

    
    # First we need to discover all the sub algorithms before checking if they are valid, incase one of them calls another
    def verify_s_algo_names(self, s_algos: list[SubAlgorithm]):
        for s_algo in s_algos:
            s_algo_name = s_algo.name.value
            
            if s_algo_name in self.C_KEYWORDS:
                e = CKeywordError(s_algo.name)
                self.add_error(e)
            elif s_algo_name in self.custom_types:
                e = IdRedefinitionError(self.custom_types[s_algo_name].name, s_algo.name)
                self.add_error(e)                
            elif s_algo_name in self.sous_algos:
                original_algo = self.sous_algos[s_algo_name]
                e = SubAlgoRedefinitionError(original_algo, s_algo)
                self.add_error(e)
            else:
                self.sous_algos[s_algo_name] = s_algo


    def verify_main_algo_and_get_variables(self, main_algo: MainAlgorithm) -> AlgorithmVariables:
        main_algo_variables = self.verify_variable_declarations(main_algo.variable_declarations, [], [])

        for statement in main_algo.statements:
            self.verify_statement(statement, main_algo_variables)

        return main_algo_variables
            

    def verify_statement(self, statement: Statement, algo_variables: AlgorithmVariables):
        if isinstance(statement, AssignmentStatement):
            self.verify_assignment_statement(statement, algo_variables)
            return

        if isinstance(statement, PourStatement):
            self.verify_pour_statement(statement, algo_variables)
            return

        if isinstance(statement, TantQueStatement):
            self.verify_tant_que_statement(statement, algo_variables)
            return

        if isinstance(statement, SiStatement):
            self.verify_si_statement(statement, algo_variables)
            return

        if isinstance(statement, FunctionStatement):
            self.verify_function_statement(statement, algo_variables)
            return

        raise Exception("")


    def verify_assignment_statement(self, assignment_statement: AssignmentStatement, algo_variables: AlgorithmVariables):
        left = assignment_statement.left
        right = assignment_statement.right

        right_type = self.verify_expression_and_get_type(right, algo_variables)
        
        if not left.is_assignable:
            e = NonAssignableExpressionError(left)
            self.add_error(e)
            return

        left_type = self.verify_expression_and_get_type(left, algo_variables)

        if left_type is None or right_type is None:
            return

        if isinstance(left_type, TableType):
            e = TableAssignmentError(left, left_type)
            self.add_error(e)
            return

        if not self.is_compatible_type(left_type, right_type, cast_entier_to_reel=True):
            e = IncompatibleAssignmentTypesError(left, left_type, right, right_type)
            self.add_error(e)




    def verify_pour_statement(self, pour_statement: PourStatement, algo_variables: AlgorithmVariables):
        iter_var_id = pour_statement.variable
        start = pour_statement.start
        end = pour_statement.end

        iter_var_type = self.verify_id_and_get_type(iter_var_id, algo_variables)
        start_type = self.verify_expression_and_get_type(start, algo_variables)
        end_type = self.verify_expression_and_get_type(end, algo_variables)
        
        if iter_var_type is not None and not self.is_entier(iter_var_type):
            e = NonIntegerIterationVariableError(iter_var_id, iter_var_type)
            self.add_error(e)

        if start_type is not None and not self.is_entier(start_type):
            e = NonIntegerStartError(start, start_type)
            self.add_error(e)

        if end_type is not None and not self.is_entier(end_type):
            e = NonIntegerEndError(end, end_type)
            self.add_error(e)

        for statement in pour_statement.statements:
            self.verify_statement(statement, algo_variables)


    def verify_tant_que_statement(self, tant_que_statement: TantQueStatement, algo_variables: AlgorithmVariables):
        condition = tant_que_statement.condition
        condition_type = self.verify_expression_and_get_type(condition, algo_variables)
        
        if condition_type is not None and not self.is_bool(condition_type):
            e = NonBooleanWhileConditionError(condition, condition_type)
            self.add_error(e)

        for statement in tant_que_statement.statements:
            self.verify_statement(statement, algo_variables)


    def verify_si_statement(self, si_statement: SiStatement, algo_variables: AlgorithmVariables):
        conditional_blocks = si_statement.conditional_blocks
        for c_b in conditional_blocks:
            condition = c_b.condition
            condition_type = self.verify_expression_and_get_type(condition, algo_variables)
            if condition_type is not None:
                if not self.is_bool(condition_type) and not self.is_bool(condition_type):
                    e = NonBooleanIfConditionError(condition, condition_type)
                    self.add_error(e)

            for statement in c_b.statements:
                self.verify_statement(statement, algo_variables)

    
    def verify_function_statement(self, function_statement: FunctionStatement, algo_variables: AlgorithmVariables):
        function_name = function_statement.name
        inputs = function_statement.inputs
        outputs = function_statement.outputs

        undeclared = False
        if function_name.value not in self.sous_algos:
            e = UndefinedFunctionError(function_name)
            self.add_error(e)
            undeclared = True

        input_types = [self.verify_expression_and_get_type(input_expression, algo_variables) for input_expression in inputs]

        output_types = []
        for output_expression in outputs:
            if not output_expression.is_assignable:
                e = NonAssignableExpressionError(output_expression)
                self.add_error(e)
                output_types.append(None)
            else:
                output_types.append(self.verify_expression_and_get_type(output_expression, algo_variables))

        if undeclared:
            return

        s_algo = self.sous_algos[function_name.value]
        expected_input_types = [input_var.type for input_var in s_algo.inputs]
        expected_output_types = [output_var.type for output_var in s_algo.outputs]

        if len(input_types) != len(expected_input_types):
            e = UnmatchedNumberOfInputsError(function_name, len(input_types), len(expected_input_types))
            self.add_error(e)
        else:
            for in_expr, in_type, exp_in_type in zip(inputs, input_types, expected_input_types):
                if in_type is not None and not self.is_compatible_type(exp_in_type, in_type, cast_entier_to_reel=True):
                    e = IncompatibleInputTypeError(in_expr, in_type, exp_in_type)
                    self.add_error(e)


        
        if len(output_types) != len(expected_output_types):
            e = UnmatchedNumberOfOutputsError(function_name, len(output_types), len(expected_output_types))
            self.add_error(e)
        else:
            for out_expr, out_type, exp_out_type in zip(outputs, output_types, expected_output_types):
                if out_type is not None and not self.is_compatible_type(out_type, exp_out_type):
                    e = IncompatibleOutputTypeError(out_expr, out_type, exp_out_type)
                    self.add_error(e)
        

        


    def verify_sub_algo_and_get_variables(self, sub_algo: SubAlgorithm):
        sub_algo_variables = self.verify_variable_declarations(sub_algo.variable_declarations, sub_algo.inputs, sub_algo.outputs)

        for statement in sub_algo.statements:
            self.verify_statement(statement, sub_algo_variables)

        return sub_algo_variables

    def verify_variable_declarations(self, 
                                     variable_declarations: list[VariableDeclaration],
                                     input_declarations: list[VariableDeclaration],
                                     output_declarations: list[VariableDeclaration]) -> AlgorithmVariables:

        variables: dict[str, VariableType] = {}
        inputs: dict[str, VariableType] = {}
        outputs: dict[str, VariableType] = {}

        ids: dict[str, ID] = {}

        for var_decl in variable_declarations:
            var_type = var_decl.type
            self.verify_var_type(var_type)

            var_id = var_decl.name
            var_name = var_id.value
            if var_name in self.C_KEYWORDS:
                e = CKeywordError(var_id)
                self.add_error(e)
            elif var_name in self.custom_types:
                e = IdRedefinitionError(self.custom_types[var_name].name, var_id)
                self.add_error(e)
            elif var_name in variables:
                original_id = ids[var_name]
                e = VariableRedeclarationError(original_id, var_id)
                self.add_error(e)
            else:
                variables[var_name] = var_type
                ids[var_name] = var_id

        for input_decl in input_declarations:
            var_type = input_decl.type
            self.verify_var_type(var_type, False)

            var_id = input_decl.name
            var_name = var_id.value
            if var_name in self.C_KEYWORDS:
                e = CKeywordError(var_id)
                self.add_error(e)
            elif var_name in self.custom_types:
                e = IdRedefinitionError(self.custom_types[var_name].name, var_id)
                self.add_error(e)
            elif var_name in inputs:
                original_id = ids[var_name]
                e = VariableRedeclarationError(original_id, var_id)
                self.add_error(e)
            else:
                inputs[var_name] = var_type
                ids[var_name] = var_id

        for output_decl in output_declarations:
            var_type = output_decl.type
            self.verify_var_type(var_type, False)

            var_id = output_decl.name
            var_name = var_id.value
            if var_name in self.C_KEYWORDS:
                e = CKeywordError(var_id)
                self.add_error(e)
            elif var_name in self.custom_types:
                e = IdRedefinitionError(self.custom_types[var_name].name, var_id)
                self.add_error(e)
            elif var_name in outputs:
                original_id = ids[var_name]
                e = VariableRedeclarationError(original_id, var_id)
                self.add_error(e)
            else:
                outputs[var_name] = var_type
                ids[var_name] = var_id

        return AlgorithmVariables(variables, inputs, outputs)

    @staticmethod
    def is_entier(var_type: VariableType) -> bool:
        return isinstance(var_type, BaseType) and var_type.value == ENTIER_T

    @staticmethod
    def is_reel(var_type: VariableType, cast=True) -> bool:

        # If we can implicitly cast an integer to a float
        if cast and MySemantics.is_entier(var_type):
            return True
        return isinstance(var_type, BaseType) and var_type.value == REEL_T

    @staticmethod
    def is_bool(var_type: VariableType) -> bool:
        return isinstance(var_type, BaseType) and var_type.value == BOOLEEN_T

    def verify_var_type(self, var_type: VariableType, table_end_must_be_defined = True) -> bool:
        if isinstance(var_type, TableType):
            is_valid = True
            for range in var_type.ranges:
                start = range.start
                end = range.end
                if table_end_must_be_defined and end is None:
                    e = TableEndNotDefinedForVariableError(start)
                    self.add_error(e)
                elif end is not None:
                    if int(end.value) <= int(start.value):
                        e = TableRangeInvalidEndError(end, description="L'indice de fin ne peut pas être inférieur ou égal à l'indice de début")
                        self.add_error(e)
                        is_valid = False

            return self.verify_var_type(var_type.type) and is_valid

        elif isinstance(var_type, PtrType):
            return self.verify_var_type(var_type.type, table_end_must_be_defined)

        elif isinstance(var_type, BaseType):
            type_value = var_type.value
            if type_value in self.BUILTIN_TYPES: return True
            if type_value in self.custom_types: return True

            if not var_type.value in self._bad_var_types:
                self._bad_var_types.add(var_type.value)
                e = UnknownBaseTypeError(var_type)
                self.add_error(e)
            

            return False

        raise Exception("Unknown node type for variable type")

    def verify_table_expression_and_get_type(self, table_expression: TableExpression, algo_variables: AlgorithmVariables) -> VariableType | None:
        table = table_expression.table_expression
        indexes = table_expression.indexes

        table_type = self.verify_expression_and_get_type(table, algo_variables)

        for index in indexes:
            index_type = self.verify_expression_and_get_type(index, algo_variables)

            if index_type is not None and not self.is_entier(index_type):
                e = NonIntegerIndexError(index, index_type)
                self.add_error(e)

        if table_type is None:
            return None

        if not isinstance(table_type, TableType):
            e = NonTableElementAccessError(table_expression, table_type)
            self.add_error(e)
            return None
    
        if len(indexes) != len(table_type.ranges):
            e = UnmatchedTableIndexesError(table, table_type, len(indexes), len(table_type.ranges))
            self.add_error(e)

        return table_type.type

    def verify_binary_operation_and_get_type(self, binary_operation: BinaryOperation, algo_variables: AlgorithmVariables) -> BaseType | None:
        left = binary_operation.left
        right = binary_operation.right
        operator = binary_operation.operator

        left_type = self.verify_expression_and_get_type(left, algo_variables)
        right_type = self.verify_expression_and_get_type(right, algo_variables)

        if left_type is None or right_type is None:
            if (isinstance(binary_operation, BinaryEq) or
                isinstance(binary_operation, BinaryLT) or
                isinstance(binary_operation, BinaryGT) or
                isinstance(binary_operation, BinaryLTE) or
                isinstance(binary_operation, BinaryGTE) or
                isinstance(binary_operation, BinaryAnd) or
                isinstance(binary_operation, BinaryOr)
                ):
                return BaseType(BOOLEEN_T)
            return None

        if isinstance(binary_operation, BinaryEq):
            if isinstance(left_type, TableType):
                e = InvalidBinaryOperationTermType(left, left_type, operator)
                self.add_error(e)

            if isinstance(right_type, TableType):
                e = InvalidBinaryOperationTermType(right, right_type, operator)
                self.add_error(e)

            if not self.is_compatible_type(left_type, right_type):
                e = DifferentTypesComparisonError(left, left_type, right, right_type, operator)
                self.add_error(e)
            return BaseType(BOOLEEN_T)

        if isinstance(binary_operation, BinaryModulo):
            if not self.is_entier(left_type):
                e = InvalidBinaryOperationTermType(left, left_type, operator, description=f"Type attendu: {BaseType('entier')}")
                self.add_error(e)
            if not self.is_entier(right_type):
                e = InvalidBinaryOperationTermType(right, right_type, operator, description=f"Type attendu: {BaseType('entier')}")
                self.add_error(e)
            return BaseType(ENTIER_T)


        if not self.is_reel(left_type, cast=True):
            e = InvalidBinaryOperationTermType(left, left_type, operator, description=f"Type attendu: {BaseType('entier')} ou {BaseType('réel')}")
            self.add_error(e)
        if not self.is_reel(right_type, cast=True):
            e = InvalidBinaryOperationTermType(right, right_type, operator, description=f"Type attendu: {BaseType('entier')} ou {BaseType('réel')}")
            self.add_error(e)


        if (isinstance(binary_operation, BinaryLT) or
            isinstance(binary_operation, BinaryGT) or
            isinstance(binary_operation, BinaryLTE) or
            isinstance(binary_operation, BinaryGTE)):
            return BaseType(BOOLEEN_T)

        if (isinstance(binary_operation, BinaryPlus) or 
            isinstance(binary_operation, BinaryMinus) or 
            isinstance(binary_operation, BinaryTimes) or 
            isinstance(binary_operation, BinaryDivide)):
            if self.is_reel(left_type, cast = False) or self.is_reel(right_type, cast = False):
                return BaseType(REEL_T)
            return BaseType(ENTIER_T)

        raise Exception("")



    def verify_expression_and_get_type(self, expression: Expression, algo_variables: AlgorithmVariables) -> VariableType | None:
        if isinstance(expression, ID):
            expression.expr_type = self.verify_id_and_get_type(expression, algo_variables)
            
        elif isinstance(expression, SubExpression):
            expression.expr_type = self.verify_expression_and_get_type(expression.expression, algo_variables)

        elif isinstance(expression, TableExpression):
            expression.expr_type = self.verify_table_expression_and_get_type(expression, algo_variables)

        elif isinstance(expression, BinaryOperation):
            expression.expr_type = self.verify_binary_operation_and_get_type(expression, algo_variables)

        elif isinstance(expression, AttributeExpression):
            expression.expr_type = self.verify_attribute_expression_and_get_type(expression, algo_variables)

        elif isinstance(expression, UnaryOperation):
            expression.expr_type = self.verify_unary_expression_and_get_type(expression, algo_variables)

        elif isinstance(expression, FunctionExpression):
            expression.expr_type = self.verify_function_expression_and_get_type(expression, algo_variables)

        elif isinstance(expression, LitInt):
            expression.expr_type = BaseType(ENTIER_T)

        elif isinstance(expression, LitFloat):
            expression.expr_type = BaseType(REEL_T)

        elif isinstance(expression, LitChar):
            expression.expr_type = BaseType(CARACTERE_T)

        elif isinstance(expression, LitBool):
            expression.expr_type = BaseType(BOOLEEN_T)

        else:
            raise Exception("Invalid node")

        return expression.expr_type
            

    def verify_id_and_get_type(self, _id: ID, algo_variables: AlgorithmVariables) -> VariableType | None:
        id_type = algo_variables.get_var_type(_id.value)
        if id_type is None:
            e = UndeclaredVariableError(_id)
            self.add_error(e)
            return None
            
        return id_type

    def is_compatible_type(self, left_type: VariableType, right_type: VariableType, cast_entier_to_reel = False) -> bool:
        if isinstance(left_type, BaseType):
            if isinstance(right_type, BaseType):
                if left_type.value == right_type.value:
                    return True
                if left_type.value == REEL_T and right_type.value == ENTIER_T:
                    return True
            return False

        if isinstance(left_type, PtrType):
            if isinstance(right_type, PtrType):
                return self.is_compatible_type(left_type.type, right_type.type)
            return False

        if isinstance(left_type, TableType):
            if isinstance(right_type, TableType):
                if len(left_type.ranges) != len(right_type.ranges):
                    return False

                if not all([l_range.is_equivalent_to(r_range) for l_range, r_range in zip(left_type.ranges, right_type.ranges)]):
                    return False
                return self.is_compatible_type(left_type.type, right_type.type)
            return False

        raise Exception("dunno how i got here")

    
    def get_attribute_type(self, custom_type_name: str, attribute_name: str) -> Optional[VariableType]:
        assert custom_type_name in self.custom_types

        t = self.custom_types[custom_type_name]
        for attr in t.attributes:
            if attr.name.value == attribute_name:
                return attr.type

        return None
            
    def verify_attribute_expression_and_get_type(self, attribute_expression: AttributeExpression, algo_variables: AlgorithmVariables) -> Optional[VariableType]:
        main_expression = attribute_expression.expression
        attribute = attribute_expression.attribute
        main_expression_type = self.verify_expression_and_get_type(main_expression, algo_variables)
        
        if main_expression_type is None:
            return None

        if not isinstance(main_expression_type, BaseType) or main_expression_type.value not in self.custom_types:
            e = NonCustomTypeAttributeAccessError(main_expression, main_expression_type)
            self.add_error(e)
            return None

        attr_value = attribute.value
        attr_type = self.get_attribute_type(main_expression_type.value, attr_value)
        if attr_type is None: 
            e = InvalidAttributError(main_expression, main_expression_type, attribute)
            self.add_error(e)
            return None

        return attr_type
        

    def verify_unary_expression_and_get_type(self, unary_expression: UnaryOperation, algo_variables: AlgorithmVariables) -> Optional[VariableType]:
        expr = unary_expression.expression

        expr_type = self.verify_expression_and_get_type(expr, algo_variables)
        if expr_type is None:
            return None

        if (isinstance(unary_expression, UnaryPlus) or
            isinstance(unary_expression, UnaryMinus)):
            if not self.is_reel(expr_type):
                e = InvalidUnaryOperationExpressionTypeError(expr, expr_type, unary_expression.operator)
                self.add_error(e)
                return None
            return expr_type

        if isinstance(unary_expression, UnaryPointer):
            return PtrType(expr_type)

        if isinstance(unary_expression, UnaryDereference):
            if not isinstance(expr_type, PtrType):
                e = NonPointerDereferenceError(expr, expr_type)
                self.add_error(e)
                return None
            return expr_type.type

        if isinstance(unary_expression, UnaryNot):
            if not self.is_bool(expr_type):
                e = NonBooleanUnaryNotError(expr, expr_type)
                self.add_error(e)
                return None
            return expr_type

        raise Exception("")

    def verify_function_expression_and_get_type(self, function_expression: FunctionExpression, algo_variables: AlgorithmVariables) -> VariableType | None:
        function_name = function_expression.name
        if function_name.value not in self.sous_algos:
            e = UndefinedFunctionError(function_name)
            self.add_error(e)
            return None

        function = self.sous_algos[function_name.value]
        expected_outputs = function.outputs
        if len(expected_outputs) != 1:
            e = NonUniqueOutputFunctionExpressionError(function_name, len(expected_outputs))
            self.add_error(e)
            return None

        inputs = function_expression.inputs
        input_types = [self.verify_expression_and_get_type(input_expression, algo_variables) for input_expression in inputs]
        expected_input_types = [input_var.type for input_var in function.inputs]

        if len(input_types) != len(expected_input_types):
            e = UnmatchedNumberOfInputsError(function_name, len(input_types), len(expected_input_types))
            self.add_error(e)
        else:
            for in_expr, in_type, exp_in_type in zip(inputs, input_types, expected_input_types):
                if in_type is not None and not self.is_compatible_type(exp_in_type, in_type, cast_entier_to_reel=True):
                    e = IncompatibleInputTypeError(in_expr, in_type, exp_in_type)
                    self.add_error(e)

        return expected_outputs[0].type

