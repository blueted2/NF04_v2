from __future__ import annotations
from email.mime import base

from parser import p_VariablesSection, p_variables_section, parser

from dataclasses import dataclass

from parser import p_ID, p_Program, p_PtrType


@dataclass
class s_Variable:
    symbol: str
    type: s_VarType


@dataclass
class s_Pointer:
    pass

@dataclass
class s_Array:
    start: int
    end: int


@dataclass
class s_VarType:
    base_type: str
    modifiers: list[s_Pointer | s_Array]


@dataclass
class s_CustomType:
    pass


def s_variables(known_types: list[str], program_vars: p_VariablesSection) -> dict[str, s_Variable]:
    variables: dict[str, s_Variable] = dict()

    for var_line in program_vars.var_lines:
        p_var_type = var_line.type

        modifiers = []

        while not isinstance(p_var_type, p_ID):
            if isinstance(p_var_type, p_PtrType):
                modifiers.append(s_Pointer())
            else:
                modifiers.append(s_Array(p_var_type.start.value, p_var_type.end.value))

            p_var_type = p_var_type.type

        base_type = p_var_type.value

        if base_type not in known_types:
            raise Exception()

        for id in var_line.id_list.id_list:
            if id.value in variables:
                raise Exception()
            
            variables[id.value] = s_Variable(id.value, s_VarType(base_type, modifiers))

    return variables


def generate_intermediate(program: p_Program):
    custom_types: dict[str, s_CustomType] = dict()
    variables: dict[str, s_Variable]

    known_types = list(custom_types.keys()) + ["int", "float"]

    variables = s_variables(known_types, program.variables_section)
    

    print(variables)


with open("program.NF04", 'r') as fp:
    text = fp.read()

tree = parser.parse(text, debug=True)

generate_intermediate(tree)