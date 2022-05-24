from typing import Optional, Tuple, cast
from ast_nodes import ID, AssignmentStatement, AttributeExpression, BaseType, BinaryOperation, CustomTypeDefinition, Expression, FunctionExpression, FunctionStatement, LitBool, LitChar, LitFloat, LitInt, MainAlgorithm, PourStatement, Program, PtrType, SiStatement, Statement, SubAlgorithm, SubExpression, TableExpression, TableRange, TableType, TantQueStatement, UnaryOperation, VariableDeclaration, VariableType
from lexer import MyLexer
from parser import MyParser
from program_variables import ProgramVariables
from semantics import MySemantics

class MyCompiler:

    C_TYPE_EQUIV = {
        "entier"   : "int",
        "réel"     : "float",
        "caractère": "char",
        "booléen"  : "bool"
    }

    def __init__(self, lexer: Optional[MyLexer] = None, parser: Optional[MyParser] = None, debug = False) -> None:
        if parser is None:
            if lexer is None: lexer = MyLexer()
            parser = MyParser(lexer, debug=debug)

        self.parser = parser

        self.program_variables: ProgramVariables
        self._requires_bool = False

    def compile(self, source_code) -> Tuple[str, list]:
        # Add an extra line return if there isn't one at the end
        if source_code[-1] != "\n":
            source_code += "\n"

        program = self.parser.parse(source_code)
        if self.parser.syntax_errors:
            return "", self.parser.syntax_errors


        semantics = MySemantics(self.parser)
        program_variables, errors = semantics.verify_program_and_get_variables_or_errors(program)

        if errors is not None:
            return "", errors

        
        self.program_variables = cast(ProgramVariables, program_variables)
        self.program = program
        code = self.generate_code()

        return code, []

    def generate_code(self) -> str:
        result = ""
        result += self.custom_types_to_str(self.program.main_algorithm.type_definitions) + "\n"
        result += self.main_algo_to_str(self.program.main_algorithm)
        for s_algo in self.program.sub_algorithms_list:
            result += self.s_algo_to_str(s_algo)
        
        if self._requires_bool:
            result = "#include <stdbool.h>\n\n" + result
            
        return result

    def custom_types_to_str(self, custom_types: list[CustomTypeDefinition]) -> str:
        result = "\n".join([self.custom_type_to_str(custom_type) for custom_type in custom_types])
        return result

    def custom_type_to_str(self, custom_type: CustomTypeDefinition) -> str:
        result = ""
        type_name = custom_type.name.value
        result += f"typedef struct {{ \n"
        result += self.indent_str(self.variable_declarations_list_to_str(custom_type.attributes)) + "\n"
        result += f"}} {type_name};\n"

        return result

    def main_algo_to_str(self, main_algo: MainAlgorithm) -> str:
        result = ""
        result += "void main() { \n"

        var_str = self.variable_declarations_list_to_str(main_algo.variable_declarations)
        var_str = self.indent_str(var_str)

        statements_str = self.statement_list_to_str(main_algo.statements)
        statements_str = self.indent_str(statements_str)

        result += var_str + "\n\n" 
        result += statements_str + "\n"

        result += "}\n"

        return result


    def s_algo_to_str(self, s_algo: SubAlgorithm) -> str:
        result = ""
        parameters = []
        for input in s_algo.inputs:
            i = 0
            parameters.append(self.variable_declaration_to_str(input, end=""))
            if isinstance(input.type, TableType):
                for range in input.type.ranges:
                    if range.end is None:
                        parameters.append(f"int _{input.name.value}_{i}")
                        i += 1
        
        output_as_return = False

        # Only add outputs to the parameters if there are more than one, or if the output a table
        if len(s_algo.outputs) > 1 or isinstance(s_algo.outputs[0].type, TableType):
            for output in s_algo.outputs:
                i = 0
                if isinstance(output.type, TableType):
                    parameters.append(self.variable_declaration_to_str(output, end=""))
                    for range in output.type.ranges:
                        if range.end is None:
                            parameters.append(f"int _{output.name.value}_{i}")
                            i += 1
                else:
                    output_as_pointer = VariableDeclaration(output.name, PtrType(output.type))
                    parameters.append(self.variable_declaration_to_str(output_as_pointer))
        else:
            output_as_return = True

        s_algo_name = s_algo.name.value

        if output_as_return:
            output_type = s_algo.outputs[0].type
            return_type_str = self.return_type_to_str(output_type)
        else:
            return_type_str = "void"

        result += f"{return_type_str} {s_algo_name} ({', '.join(parameters)}){{"

        

        return result

    def statement_list_to_str(self, statements: list[Statement]) -> str:
        return "\n".join([self.statement_to_str(statement) for statement in statements])

    def statement_to_str(self, statement: Statement) -> str:
        if isinstance(statement, AssignmentStatement):
            left_str = self.expression_to_str(statement.left)
            right_str = self.expression_to_str(statement.right)
            return f"{left_str} = {right_str};"

        if isinstance(statement, SiStatement):
            result = ""
            main_conditional, *other_conditionals = statement.conditional_blocks

            main_condition_str = self.expression_to_str(main_conditional.condition)
            main_block_str = self.statement_list_to_str(main_conditional.statements)

            main_block_str = self.indent_str(main_block_str)
            result += f"if ({main_condition_str}) {{ \n{main_block_str}\n}} "

            for conditional in other_conditionals:
                condition_str = self.expression_to_str(conditional.condition)
                block_str = self.statement_list_to_str(conditional.statements)
                block_str = self.indent_str(block_str)

                result += f"elif ({condition_str}) {{ \n{block_str}\n}} "

            if len(statement.default_block) != 0:
                default_block_str = self.statement_list_to_str(statement.default_block)
                default_block_str = self.indent_str(default_block_str)
                
                result += f"else {{\n{default_block_str}\n}}"
            return result

        if isinstance(statement, PourStatement):
            result = ""
            
            step = int(statement.step.value) if statement.step is not None else 1
            iter_var = statement.variable.value
            start_expr = statement.start
            end_expr = statement.end

            start_str = self.expression_to_str(start_expr)
            end_str = self.expression_to_str(end_expr)

            # Infinite loop if step = 0, but that's the programmer's fault xD
            if step >= 0:
                for_header = f"for (int {iter_var} = {start_str}; {iter_var} < {end_str}; {iter_var} += {step})"
            else:
                for_header = f"for (int {iter_var} = {start_str}; {iter_var} > {end_str}; {iter_var} -= {-step})"
            
            block_str = self.statement_list_to_str(statement.statements)
            block_str = self.indent_str(block_str)

            return f"{for_header} {{\n{block_str}\n}}"

        if isinstance(statement, TantQueStatement):
            condition_str = self.expression_to_str(statement.condition)
            block_str = self.indent_str(self.statement_list_to_str(statement.statements))

            return f"while ({condition_str}) {{\n{block_str}\n}}"

        if isinstance(statement, FunctionStatement):
            function_name = statement.name.value
            s_algo = self.program_variables.sub_algorithms[function_name]
            inputs = statement.inputs
            outputs = statement.outputs
            expected_inputs = s_algo.inputs
            expected_outputs = s_algo.outputs

            arguments = ""

            input_strs = []
            for input, exp_input in zip(inputs, expected_inputs):
                input_strs.append(self.expression_to_str(input))
                input_type = input.expr_type
                if isinstance(input_type, TableType):
                    exp_input_type = cast(TableType, exp_input.type)
                    for range, exp_range in zip(input_type.ranges, exp_input_type.ranges):
                        if exp_range.end is None:
                            start = int(range.start.value)
                            end = int(cast(LitInt, range.end).value)
                            input_strs.append(str(end - start))
                

            output_strs = []
            for output, exp_output in zip(outputs, expected_outputs):
                output_type = output.expr_type
                if isinstance(output_type, TableType):
                    exp_output_type = cast(TableType, exp_output.type)
                    output_strs.append(self.expression_to_str(output))
                    for range, exp_range in zip(output_type.ranges, exp_output_type.ranges):
                        if exp_range.end is None:
                            start = int(range.start.value)
                            end = int(cast(LitInt, range.end).value)
                            output_strs.append(str(end - start))

                else:
                    output_strs.append(f"&{self.expression_to_str(output)}")

            arguments = ", ".join(input_strs + output_strs)

            result = f"{function_name} ({arguments});"

            return result

        raise Exception("")



    def get_nb_table_elements(self, table_type: TableType) -> int:
        size = 1
        for range in table_type.ranges:
            assert range.end is not None
            size *= (int(range.end.value) - int(range.start.value))
        return size 


    def expression_to_str(self, expression: Expression) -> str:
        if isinstance(expression, ID):
            return expression.value
        if isinstance(expression, LitInt):
            return expression.value
        if isinstance(expression, LitFloat):
            return expression.value
        if isinstance(expression, LitChar):
            return f'{expression.value}'
        if isinstance(expression, LitBool):
            self._requires_bool = True
            v = expression.value.lower()
            return "true" if v == "Vrai" else "false"

        if isinstance(expression, BinaryOperation):
            left_str = self.expression_to_str(expression.left)
            right_str = self.expression_to_str(expression.right)
            operator_str = expression.operator.operator
            return f"{left_str} {operator_str} {right_str}"

        if isinstance(expression, UnaryOperation):
            expr_str = self.expression_to_str(expression.expression)
            operator_str = expression.operator.operator 
            if operator_str == "non":
                operator_str = "!"
            elif operator_str == "^":
                operator_str = "*"
            return f"{operator_str}{expr_str}"

        if isinstance(expression, SubExpression):
            expr_str = self.expression_to_str(expression.expression)
            return f"({expr_str})"
        
        if isinstance(expression, TableExpression):
            result = ""
            table_expression = expression.table_expression
            table_indexes = expression.indexes
            table_expression_str = self.expression_to_str(table_expression)
            result += table_expression_str

            table_expression_type = cast(TableType, table_expression.expr_type)
            for range, index_expr in zip(table_expression_type.ranges, table_indexes):
                index_str = self.expression_to_str(index_expr)
                if int(range.start.value) == 0:
                    result += f"[{index_str}]"
                else:
                    result += f"[{index_str} - {range.start.value}]"
                
            return result

        if isinstance(expression, AttributeExpression):
            main_expr = expression.expression
            attribute = expression.attribute
            main_expr_str = self.expression_to_str(main_expr)
            return f"{main_expr_str}.{attribute.value}"            


        if isinstance(expression, FunctionExpression):
            result = ""
            function_name = expression.name.value
            inputs = expression.inputs
            expected_inputs = self.program_variables.sub_algorithms[function_name].inputs

            input_strs = []
            for input, exp_input in zip(inputs, expected_inputs):
                input_strs.append(self.expression_to_str(input))
                input_type = input.expr_type
                if isinstance(input_type, TableType):
                    exp_input_type = cast(TableType, exp_input.type)
                    for range, exp_range in zip(input_type.ranges, exp_input_type.ranges):
                        if exp_range.end is None:
                            start = int(range.start.value)
                            end = int(cast(LitInt, range.end).value)
                            input_strs.append(str(end - start))

            result += f"{function_name}("
            result += ", ".join(input_strs)
            result += ")"
            return result

        raise Exception("")


    def variable_declarations_list_to_str(self, var_decl_list: list[VariableDeclaration], end=";", join="\n") -> str:
        return join.join([self.variable_declaration_to_str(var_decl, end=end) for var_decl in var_decl_list])




    def variable_declaration_to_str(self, var_decl: VariableDeclaration, end=";") -> str:
        result = "{}"
        var_name = var_decl.name.value
        var_type = var_decl.type

        previous = ""

        curr_var_type = var_type
        while not isinstance(curr_var_type, BaseType):
            if isinstance(curr_var_type, TableType):
                ranges = self.table_ranges_to_str(curr_var_type.ranges, var_decl.name.value)
                if previous == "ptr":
                    result = f"({{}}){ranges}".format(result)
                else:
                    result = f"{{}}{ranges}".format(result)
                previous = "tab"
            elif isinstance(curr_var_type, PtrType):
                if previous == "tab":
                    result = f"(*{{}})".format(result)
                else:
                    result = f"*{{}}".format(result)
                previous = "ptr"
            curr_var_type = curr_var_type.type

        result = result.format(var_name)

        var_type_name = curr_var_type.value
        if var_type_name in self.C_TYPE_EQUIV:
            var_type_name = self.C_TYPE_EQUIV[var_type_name]
            if var_type_name == "bool":
                self._requires_bool = True

        result = f"{var_type_name} {result}{end}"
        return result

    def return_type_to_str(self, var_type: VariableType) -> str:
        if isinstance(var_type, BaseType):
            var_type_name = var_type.value
            if var_type_name in self.C_TYPE_EQUIV:
                var_type_name = self.C_TYPE_EQUIV[var_type_name]
                if var_type_name == "bool":
                    self._requires_bool = True
            return var_type_name

        if isinstance(var_type, PtrType) or isinstance(var_type, TableType):
            return self.return_type_to_str(var_type.type) + "*"

        raise Exception("")

            
    def table_ranges_to_str(self, table_ranges: list[TableRange], tab_name: str) -> str:
        result = ""
        i = 0
        for t_r in table_ranges:
            if t_r.end is None:
                result += f"[_{tab_name}_{i}]"
                i += 1
            else:
                if int(t_r.start.value) == 0:
                    result += f"[{int(t_r.end.value)}]"
                else:
                    result += f"[{int(t_r.end.value)} - {int(t_r.start.value)}]"

        return result

    def indent_str(self, string: str, indent="  ") -> str:
        return indent + string.replace("\n", "\n" + indent)

if __name__ == "__main__":
    with open("program.NF04", encoding='utf-8') as fp:
        source_code = fp.read()

    compiler = MyCompiler(debug = False)

    result, errors = compiler.compile(source_code)

    for error in errors:
        print(error)
        print()

    with open("output.c", 'w') as fp:
        fp.write(result)
