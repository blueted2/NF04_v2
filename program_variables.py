from __future__ import annotations
from dataclasses import dataclass
from ast_nodes import SubAlgorithm, VariableType

@dataclass
class ProgramVariables:
    main_algorithm_variables: AlgorithmVariables
    sub_algorithm_variables: dict[str, AlgorithmVariables]
    sub_algorithms: dict[str, SubAlgorithm]
    

@dataclass
class AlgorithmVariables:
    inputs: dict[str, VariableType]
    outputs: dict[str, VariableType]
    variables: dict[str, VariableType]

    def var_is_defined(self, var_name: str):
        return var_name in self.inputs or var_name in self.outputs or var_name in self.variables

    def get_var_type(self, var: str) -> VariableType | None:
        if var in self.variables: return self.variables[var]
        if var in self.inputs:  return self.inputs[var]
        if var in self.outputs: return self.outputs[var]
        
        return None