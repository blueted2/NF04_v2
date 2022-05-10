from __future__ import annotations
from enum import Enum
from xmlrpc.client import Boolean
from ast_nodes import ASTNode, BaseType, ComplexType, LitInt, PtrType, SubAlgorithm, TableType

from typing import Any, Optional, Tuple
from ast_nodes import Program
from errors import SemanticError, TableRangeError, TableRangeInvalidEndError
from parser import MyParser
from utils import get_column


class VariableScopeType(Enum):
    LOCAL_VARIABLE = 0
    INPUT_VARIALBE = 1
    OUTPUT_VARIABLE = 2


class MySemantics:
    BUILTIN_TYPES = ["réel", "reel", "entier", "booleen", "booléen", "bool", "caractère", "caractere"]
    def __init__(self, parser: MyParser) -> None:
        self.parser = parser
        self.global_symbols: dict[str, Any] = {}
        self.semantic_errors: list = []

        # self.types: dict[str, Any] = {}
        # self.sous_algos: dict[str, SubAlgorithm] = {}

        # self.variables: dict[str, ComplexType]
    
    def add_error(self, error: SemanticError):
        self.semantic_errors.append(error)
        print(error)


    def verify_semantics(self, program: Program) -> Tuple[bool, list]:
        # TODO: Handle adding custom types

        # Sub algos
        for s_algo in program.sub_algorithms_list:
            s_algo_name = s_algo.name.value
            if s_algo_name not in self.global_symbols:
                self.global_symbols[s_algo_name] = s_algo
            else:
                raise Exception("Handle trying to add s_algo multiple times")

        # Main algo variables
        main_algo_variables: dict[str, ComplexType] = {}

        # For each line of variable declarations:
        # - check that the variable type is valid (eg. if table, check start/end...)
        # - check that the variables names don't already exist
        for var_decl_line in program.main_algorithm.variable_declarations:
            var_type = var_decl_line.type
            self.validate_var_type(var_type)
            for id in var_decl_line.names:
                var_name = id.value
                if var_name not in main_algo_variables:
                    main_algo_variables[var_name] = var_type
                else:
                    original_id = main_algo_variables[var_name]
                    raise Exception("Handle variable error")

        # Sub algo variables
        for s_algo in program.sub_algorithms_list:
            s_algo_variables: dict[str, Any] = {}
            var_decls = s_algo.inputs + s_algo.outputs + s_algo.variable_declarations
            for var_decl_line in var_decls:
                var_type = var_decl_line.type
                self.validate_var_type(var_type)
                for id in var_decl_line.names:
                    var_name = id.value
                    if var_name not in s_algo_variables:
                        s_algo_variables[var_name] = var_type
                    else:
                        raise Exception("Handle variable error")

        return True, []

    def validate_var_type(self, var_type: ComplexType) -> None:
        if isinstance(var_type, TableType):
            for range in var_type.ranges:
                start, end = range
                if end is not None:
                    if end.value <= start.value:
                        e = TableRangeInvalidEndError(end, description="L'indice de fin ne peut pas être inférieur ou égal à l'indice de début")
                        self.add_error(e)

            self.validate_var_type(var_type.type)

        elif isinstance(var_type, PtrType):
            self.validate_var_type(var_type.type)

    

    def assert_node_type(self, node: ASTNode, expected: type):
        if isinstance(node, expected): return

        print(f"Expected {expected}, got {node}")
        self.semantic_errors.append(node)


# class VariableScope:
#     def __init__(self, parent_scope: Optional[VariableScope] = None) -> None:
#         self.parent_scope = parent_scope

#         self.variables = {}
#         self.inputs = {}
#         self.outputs = {}


#     def is_defined(self, var_name: str) -> bool:
#         if var_name in self.variables.keys():
#             return True

#         if var_name in self.inputs.keys():
#             return True

#         if var_name in self.outputs.keys():
#             return True

#         return False


#     def try_add_variable(self, var_name: str, var_type: ComplexType, scope_type: VariableScopeType = VariableScopeType.LOCAL_VARIABLE) -> bool:
#         if self.is_defined(var_name):
#             return False
        
#         if scope_type == VariableScopeType.INPUT_VARIALBE:
#             self.inputs[var_name] = var_type
#         elif scope_type == VariableScopeType.OUTPUT_VARIABLE:
#             self.outputs[var_name] = var_type
#         else:
#             self.variables[var_name] = var_type

#         return True


        

