from typing import Union, get_args, get_origin

from classiq.qmod.symbolic_expr import Symbolic

SymbolicTypes = Union[
    Symbolic, int, float, bool, tuple["SymbolicTypes", ...], list["SymbolicTypes"]
]
SYMBOLIC_TYPES = tuple(get_origin(t) or t for t in get_args(SymbolicTypes))
