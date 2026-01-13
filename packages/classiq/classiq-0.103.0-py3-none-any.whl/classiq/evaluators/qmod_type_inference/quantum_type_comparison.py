from classiq.interface.exceptions import (
    ClassiqInternalExpansionError,
)
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.type_name import TypeName
from classiq.interface.model.quantum_type import (
    QuantumBit,
    QuantumBitvector,
    QuantumNumeric,
    QuantumType,
)


def _compare_expressions(expr1: Expression | None, expr2: Expression | None) -> bool:
    if expr1 is None:
        return expr2 is None
    if expr2 is None:
        return False
    return expr1.expr == expr2.expr


def compare_quantum_types(type_1: QuantumType, type_2: QuantumType) -> bool:
    for qmod_type in (type_1, type_2):
        if isinstance(qmod_type, TypeName) and not qmod_type.has_fields:
            raise ClassiqInternalExpansionError("Quantum struct expected")
    if isinstance(type_1, QuantumBit):
        return isinstance(type_2, QuantumBit)
    if isinstance(type_1, QuantumNumeric):
        return (
            isinstance(type_2, QuantumNumeric)
            and _compare_expressions(type_1.size, type_2.size)
            and _compare_expressions(type_1.is_signed, type_2.is_signed)
            and _compare_expressions(type_1.fraction_digits, type_2.fraction_digits)
        )
    if isinstance(type_1, QuantumBitvector):
        return (
            isinstance(type_2, QuantumBitvector)
            and _compare_expressions(type_1.length, type_2.length)
            and compare_quantum_types(type_1.element_type, type_2.element_type)
        )
    if isinstance(type_1, TypeName):
        return (
            isinstance(type_2, TypeName)
            and type_1.name == type_2.name
            and all(
                compare_quantum_types(field_type_1, field_type_2)
                for field_type_1, field_type_2 in zip(
                    type_1.fields.values(), type_2.fields.values(), strict=True
                )
            )
        )
    raise ClassiqInternalExpansionError(f"Unexpected type {type(type_1).__name__}")
