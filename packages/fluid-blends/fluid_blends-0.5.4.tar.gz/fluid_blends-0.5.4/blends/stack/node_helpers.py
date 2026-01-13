from blends.models import (
    NId,
)
from blends.stack.attributes import (
    STACK_GRAPH_IS_EXPORTED,
    STACK_GRAPH_KIND,
    STACK_GRAPH_PRECEDENCE,
    STACK_GRAPH_SCOPE,
    STACK_GRAPH_SYMBOL,
)
from blends.stack.node_kinds import (
    StackGraphNodeKind,
)

StackGraphNodeAttributes = dict[str, object]


def push_symbol_node_attributes(*, symbol: str, precedence: int = 0) -> StackGraphNodeAttributes:
    return {
        STACK_GRAPH_KIND: StackGraphNodeKind.PUSH_SYMBOL.value,
        STACK_GRAPH_SYMBOL: symbol,
        STACK_GRAPH_SCOPE: None,
        STACK_GRAPH_PRECEDENCE: precedence,
        STACK_GRAPH_IS_EXPORTED: False,
    }


def push_scoped_symbol_node_attributes(
    *,
    symbol: str,
    scope: NId,
    precedence: int = 0,
) -> StackGraphNodeAttributes:
    return {
        STACK_GRAPH_KIND: StackGraphNodeKind.PUSH_SCOPED_SYMBOL.value,
        STACK_GRAPH_SYMBOL: symbol,
        STACK_GRAPH_SCOPE: scope,
        STACK_GRAPH_PRECEDENCE: precedence,
        STACK_GRAPH_IS_EXPORTED: False,
    }


def pop_symbol_node_attributes(*, symbol: str, precedence: int = 0) -> StackGraphNodeAttributes:
    return {
        STACK_GRAPH_KIND: StackGraphNodeKind.POP_SYMBOL.value,
        STACK_GRAPH_SYMBOL: symbol,
        STACK_GRAPH_SCOPE: None,
        STACK_GRAPH_PRECEDENCE: precedence,
        STACK_GRAPH_IS_EXPORTED: False,
    }


def pop_scoped_symbol_node_attributes(
    *, symbol: str, precedence: int = 0
) -> StackGraphNodeAttributes:
    return {
        STACK_GRAPH_KIND: StackGraphNodeKind.POP_SCOPED_SYMBOL.value,
        STACK_GRAPH_SYMBOL: symbol,
        STACK_GRAPH_SCOPE: None,
        STACK_GRAPH_PRECEDENCE: precedence,
        STACK_GRAPH_IS_EXPORTED: False,
    }


def scope_node_attributes(*, is_exported: bool) -> StackGraphNodeAttributes:
    return {
        STACK_GRAPH_KIND: StackGraphNodeKind.SCOPE.value,
        STACK_GRAPH_SYMBOL: None,
        STACK_GRAPH_SCOPE: None,
        STACK_GRAPH_PRECEDENCE: 0,
        STACK_GRAPH_IS_EXPORTED: is_exported,
    }


def root_node_attributes() -> StackGraphNodeAttributes:
    return {
        STACK_GRAPH_KIND: StackGraphNodeKind.ROOT.value,
        STACK_GRAPH_SYMBOL: None,
        STACK_GRAPH_SCOPE: None,
        STACK_GRAPH_PRECEDENCE: 0,
        STACK_GRAPH_IS_EXPORTED: False,
    }


def jump_to_node_attributes() -> StackGraphNodeAttributes:
    return {
        STACK_GRAPH_KIND: StackGraphNodeKind.JUMP_TO.value,
        STACK_GRAPH_SYMBOL: None,
        STACK_GRAPH_SCOPE: None,
        STACK_GRAPH_PRECEDENCE: 0,
        STACK_GRAPH_IS_EXPORTED: False,
    }


def drop_scopes_node_attributes() -> StackGraphNodeAttributes:
    return {
        STACK_GRAPH_KIND: StackGraphNodeKind.DROP_SCOPES.value,
        STACK_GRAPH_SYMBOL: None,
        STACK_GRAPH_SCOPE: None,
        STACK_GRAPH_PRECEDENCE: 0,
        STACK_GRAPH_IS_EXPORTED: False,
    }
