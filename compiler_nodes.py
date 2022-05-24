from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Program:
    custom_types: dict[str, CustomType]
    main_algorithm: 

@dataclass
class CustomType:
    attributes: dict[str, Type]

@dataclass
class FullyDefinedType: pass

@dataclass
class Type: pass

@dataclass
class PointerType(Type):
    points_to: Type


@dataclass
class 



@dataclass
class Algorithm:
    variables: dict[str, FullyDefinedType]
    inputs: dict[str, Type]
    outputs: dict[str, Type]
    statements: list[Statement]

@dataclass
class Statement:
