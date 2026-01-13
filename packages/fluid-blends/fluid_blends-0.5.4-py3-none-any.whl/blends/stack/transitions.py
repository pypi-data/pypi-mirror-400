from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from blends.stack.node_kinds import (
    StackGraphNodeKind,
)
from blends.stack.stacks import (
    ScopeStackNode,
    StackState,
    SymbolStackNode,
)

if TYPE_CHECKING:
    from blends.stack.view import (
        StackGraphView,
    )


class TransitionError(str, Enum):
    EMPTY_SCOPE_STACK = "EmptyScopeStack"
    EMPTY_SYMBOL_STACK = "EmptySymbolStack"
    INCORRECT_POPPED_SYMBOL = "IncorrectPoppedSymbol"
    MISSING_ATTACHED_SCOPE_LIST = "MissingAttachedScopeList"
    UNEXPECTED_ATTACHED_SCOPE_LIST = "UnexpectedAttachedScopeList"
    UNKNOWN_ATTACHED_SCOPE = "UnknownAttachedScope"
    MISSING_SCOPE_PAYLOAD = "MissingScopePayload"
    MISSING_SYMBOL_PAYLOAD = "MissingSymbolPayload"
    UNKNOWN_NODE_KIND = "UnknownNodeKind"


@dataclass(frozen=True, slots=True)
class TransitionResult:
    state: StackState
    jump_target: int | None
    error: TransitionError | None


def _handle_push_symbol(
    view: StackGraphView, node_index: int, state: StackState
) -> TransitionResult:
    sym = view.symbol_id_at(node_index)
    if sym is None:
        return TransitionResult(state, None, TransitionError.MISSING_SYMBOL_PAYLOAD)
    new_symbol_stack = SymbolStackNode(symbol_id=sym, scopes=None, tail=state.symbol_stack)
    return TransitionResult(StackState(new_symbol_stack, state.scope_stack), None, None)


def _handle_pop_symbol(
    view: StackGraphView, node_index: int, state: StackState
) -> TransitionResult:
    sym = view.symbol_id_at(node_index)
    if sym is None:
        return TransitionResult(state, None, TransitionError.MISSING_SYMBOL_PAYLOAD)
    top = state.symbol_stack
    if top is None:
        return TransitionResult(state, None, TransitionError.EMPTY_SYMBOL_STACK)
    if top.symbol_id != sym:
        return TransitionResult(state, None, TransitionError.INCORRECT_POPPED_SYMBOL)
    if top.scopes is not None:
        return TransitionResult(state, None, TransitionError.UNEXPECTED_ATTACHED_SCOPE_LIST)
    return TransitionResult(StackState(top.tail, state.scope_stack), None, None)


def _handle_drop_scopes(
    _view: StackGraphView, _node_index: int, state: StackState
) -> TransitionResult:
    return TransitionResult(StackState(state.symbol_stack, None), None, None)


def _handle_jump_to(_view: StackGraphView, _node_index: int, state: StackState) -> TransitionResult:
    top = state.scope_stack
    if top is None:
        return TransitionResult(state, None, TransitionError.EMPTY_SCOPE_STACK)
    jump_target = top.scope_index
    return TransitionResult(StackState(state.symbol_stack, top.tail), jump_target, None)


def _handle_push_scoped_symbol(
    view: StackGraphView, node_index: int, state: StackState
) -> TransitionResult:
    sym = view.symbol_id_at(node_index)
    if sym is None:
        return TransitionResult(state, None, TransitionError.MISSING_SYMBOL_PAYLOAD)
    attached_scope = view.scope_index_at(node_index)
    if attached_scope is None:
        return TransitionResult(state, None, TransitionError.MISSING_SCOPE_PAYLOAD)
    if attached_scope not in view.exported_scopes:
        return TransitionResult(state, None, TransitionError.UNKNOWN_ATTACHED_SCOPE)
    attached_scopes = ScopeStackNode(scope_index=attached_scope, tail=state.scope_stack)
    new_symbol_stack = SymbolStackNode(
        symbol_id=sym,
        scopes=attached_scopes,
        tail=state.symbol_stack,
    )
    return TransitionResult(StackState(new_symbol_stack, state.scope_stack), None, None)


def _handle_pop_scoped_symbol(
    view: StackGraphView, node_index: int, state: StackState
) -> TransitionResult:
    sym = view.symbol_id_at(node_index)
    if sym is None:
        return TransitionResult(state, None, TransitionError.MISSING_SYMBOL_PAYLOAD)
    top = state.symbol_stack
    if top is None:
        return TransitionResult(state, None, TransitionError.EMPTY_SYMBOL_STACK)
    if top.symbol_id != sym:
        return TransitionResult(state, None, TransitionError.INCORRECT_POPPED_SYMBOL)
    if top.scopes is None:
        return TransitionResult(state, None, TransitionError.MISSING_ATTACHED_SCOPE_LIST)
    return TransitionResult(StackState(top.tail, top.scopes), None, None)


def _handle_noop(_view: StackGraphView, _node_index: int, state: StackState) -> TransitionResult:
    return TransitionResult(state, None, None)


def apply_node(view: StackGraphView, node_index: int, state: StackState) -> TransitionResult:
    kind = view.kind_at(node_index)
    handler = {
        StackGraphNodeKind.DROP_SCOPES.value: _handle_drop_scopes,
        StackGraphNodeKind.JUMP_TO.value: _handle_jump_to,
        StackGraphNodeKind.POP_SCOPED_SYMBOL.value: _handle_pop_scoped_symbol,
        StackGraphNodeKind.POP_SYMBOL.value: _handle_pop_symbol,
        StackGraphNodeKind.PUSH_SCOPED_SYMBOL.value: _handle_push_scoped_symbol,
        StackGraphNodeKind.PUSH_SYMBOL.value: _handle_push_symbol,
        StackGraphNodeKind.ROOT.value: _handle_noop,
        StackGraphNodeKind.SCOPE.value: _handle_noop,
    }.get(kind)
    if handler is None:
        return TransitionResult(state, None, TransitionError.UNKNOWN_NODE_KIND)
    return handler(view, node_index, state)
