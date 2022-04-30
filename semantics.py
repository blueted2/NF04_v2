from __future__ import annotations
from enum import Enum

from typing import Optional, Tuple
from ast_nodes import Program, ComplexType


class VariableScopeType(Enum):
    LOCAL_VARIABLE = 0
    INPUT_VARIALBE = 1
    OUTPUT_VARIABLE = 2


class MySemantics:
    def __init__(self) -> None:
        self.program_scope = VariableScope()
        self.semantic_errors: list = []
    

    def verify_semantics(self, program: Program) -> Tuple[bool, list]:
        return True, []
        variable_declarations = program.main_algorithm.variable_declarations

        for var_decl_line in variable_declarations:
            names = var_decl_line.names
            type = var_decl_line.type

            for var_name in names:
                if self.program_scope.is_defined(var_name):
                    return False, []

                self.program_scope.try_add_variable(var_name, type)

                

        return True, []


    def add_error(self, error):
        self.semantic_errors.append(error)
        print(error)


class VariableScope:
    def __init__(self, parent_scope: Optional[VariableScope] = None) -> None:
        self.parent_scope = parent_scope

        self.variables = {}
        self.inputs = {}
        self.outputs = {}


    def is_defined(self, var_name: str) -> bool:
        if var_name in self.variables.keys():
            return True

        if var_name in self.inputs.keys():
            return True

        if var_name in self.outputs.keys():
            return True

        return False


    def try_add_variable(self, var_name: str, var_type: ComplexType, scope_type: VariableScopeType = VariableScopeType.LOCAL_VARIABLE) -> bool:
        if self.is_defined(var_name):
            return False
        
        if scope_type == VariableScopeType.INPUT_VARIALBE:
            self.inputs[var_name] = var_type
        elif scope_type == VariableScopeType.OUTPUT_VARIABLE:
            self.outputs[var_name] = var_type
        else:
            self.variables[var_name] = var_type

        return True


        

