from typing import Any

from classiq.interface.ast_node import ASTNode
from classiq.interface.debug_info.debug_info import DebugInfoCollection
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import ClassicalType
from classiq.interface.generator.functions.type_modifier import TypeModifier
from classiq.interface.generator.visitor import Transformer, Visitor
from classiq.interface.model.handle_binding import HandleBinding
from classiq.interface.model.model import Model
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.port_declaration import (
    PortDeclaration,
)
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)

from classiq.model_expansions.utils.counted_name_allocator import CountedNameAllocator


class ModelNormalizer(Visitor):
    def __init__(
        self,
        normalize_func_names: bool = False,
        normalize_quantum_var_names: bool = False,
    ) -> None:
        self._normalize_func_names = normalize_func_names
        self._normalize_quantum_var_names = normalize_quantum_var_names
        self._funcs_renames: dict[str, str] = {}
        self._count_name = CountedNameAllocator()
        self.original_names: dict[str, str] = {}

    def visit(self, node: Any) -> None:
        if isinstance(node, ASTNode):
            node.model_config["frozen"] = False
            node.source_ref = None
            node.back_ref = None
            if hasattr(node, "uuid"):
                node.uuid = None
        super().visit(node)

    def visit_Model(self, model: Model) -> None:
        model.debug_info = DebugInfoCollection()
        model.functions.sort(key=lambda x: x.name)
        self._funcs_renames = {
            func.name: f"___func_{index}" for index, func in enumerate(model.functions)
        }
        self.generic_visit(model)

    def visit_NativeFunctionDefinition(self, func: NativeFunctionDefinition) -> None:
        if self._normalize_func_names:
            func.name = self._funcs_renames[func.name]
        self.generic_visit(func)

    def visit_QuantumFunctionCall(self, call: QuantumFunctionCall) -> None:
        if self._normalize_func_names:
            if isinstance(call.function, str):
                if call.function in self._funcs_renames:
                    call.function = self._funcs_renames[call.function]
            else:
                if call.function.name in self._funcs_renames:
                    call.function.name = self._funcs_renames[call.function.name]
        self.generic_visit(call)

    def visit_PortDeclaration(self, decl: PortDeclaration) -> None:
        decl.type_modifier = TypeModifier.Mutable
        self._rename_quantum_var(decl, "_port")

    def visit_VariableDeclarationStatement(
        self, var: VariableDeclarationStatement
    ) -> None:
        self._rename_quantum_var(var, "_var")

    def _rename_quantum_var(
        self, var: VariableDeclarationStatement | PortDeclaration, new_name_prefix: str
    ) -> None:
        if self._normalize_quantum_var_names:
            old_name = var.name
            var.name = self._count_name.allocate(new_name_prefix)
            self.original_names[old_name] = var.name

    def visit_HandleBinding(self, handle: HandleBinding) -> None:
        if self._normalize_quantum_var_names:
            # this is a hack use just for testing, do not use in production
            object.__setattr__(
                handle, "name", self.original_names.get(handle.name, handle.name)
            )


class ClearModelInternals(Transformer):
    def visit_Expression(self, expr: Expression) -> Expression:
        expr._evaluated_expr = None
        expr._try_to_immediate_evaluate()
        return expr

    def visit_ClassicalType(self, classical_type: ClassicalType) -> ClassicalType:
        return type(classical_type).model_validate_json(
            classical_type.model_dump_json()
        )
