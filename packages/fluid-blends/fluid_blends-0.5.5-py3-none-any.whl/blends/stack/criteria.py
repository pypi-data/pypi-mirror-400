from __future__ import annotations

from typing import TYPE_CHECKING

from blends.stack.node_kinds import (
    StackGraphNodeKind,
)

if TYPE_CHECKING:
    from blends.stack.stacks import (
        StackState,
    )
    from blends.stack.view import (
        StackGraphView,
    )


def is_reference_endpoint(view: StackGraphView, node_index: int) -> bool:
    kind = view.kind_at(node_index)
    is_push = kind in {
        StackGraphNodeKind.PUSH_SYMBOL.value,
        StackGraphNodeKind.PUSH_SCOPED_SYMBOL.value,
    }
    if not is_push:
        return False
    if node_index in {0, 1}:
        return False
    return view.node_is_reference[node_index]


def is_definition_endpoint(view: StackGraphView, node_index: int) -> bool:
    kind = view.kind_at(node_index)
    is_pop = kind in {
        StackGraphNodeKind.POP_SYMBOL.value,
        StackGraphNodeKind.POP_SCOPED_SYMBOL.value,
    }
    if not is_pop:
        return False
    if node_index in {0, 1}:
        return False
    return view.node_is_definition[node_index]


def is_exported_scope_endpoint(view: StackGraphView, node_index: int) -> bool:
    return (
        view.kind_at(node_index) == StackGraphNodeKind.SCOPE.value
        and node_index in view.exported_scopes
    )


def is_root_endpoint(view: StackGraphView, node_index: int) -> bool:
    return view.kind_at(node_index) == StackGraphNodeKind.ROOT.value


def is_jump_to_boundary(view: StackGraphView, node_index: int) -> bool:
    return view.kind_at(node_index) == StackGraphNodeKind.JUMP_TO.value


def is_endpoint(view: StackGraphView, node_index: int) -> bool:
    return (
        is_reference_endpoint(view, node_index)
        or is_definition_endpoint(view, node_index)
        or is_exported_scope_endpoint(view, node_index)
        or is_root_endpoint(view, node_index)
    )


def is_complete_definition_path(
    view: StackGraphView,
    *,
    start_node_index: int,
    end_node_index: int,
    start_state: StackState,
    end_state: StackState,
) -> bool:
    if not is_reference_endpoint(view, start_node_index):
        return False
    if not is_definition_endpoint(view, end_node_index):
        return False
    if start_state.symbol_stack is not None:
        return False
    if start_state.scope_stack is not None:
        return False
    if end_state.symbol_stack is not None:
        return False
    return end_state.scope_stack is None
