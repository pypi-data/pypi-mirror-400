from classiq.interface.exceptions import ClassiqExpansionError
from classiq.interface.model.model import Model
from classiq.interface.model.quantum_function_declaration import (
    NamedParamsQuantumFunctionDeclaration,
)


def check_function_name_collisions(
    model: Model, builtin_functions: list[NamedParamsQuantumFunctionDeclaration]
) -> None:
    redefined_functions = [
        function.name
        for function in builtin_functions
        if function.name in model.function_dict
    ]
    if len(redefined_functions) == 1:
        raise ClassiqExpansionError(
            f"Cannot redefine built-in function {redefined_functions[0]!r}"
        )
    elif len(redefined_functions) > 1:
        raise ClassiqExpansionError(
            f"Cannot redefine built-in functions: {redefined_functions}"
        )
