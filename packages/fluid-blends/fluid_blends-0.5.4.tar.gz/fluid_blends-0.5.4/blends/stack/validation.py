from collections.abc import Iterable

from blends.models import (
    Graph,
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
    is_stack_graph_kind,
)

_KINDS_WITH_SYMBOL = {
    StackGraphNodeKind.PUSH_SYMBOL.value,
    StackGraphNodeKind.PUSH_SCOPED_SYMBOL.value,
    StackGraphNodeKind.POP_SYMBOL.value,
    StackGraphNodeKind.POP_SCOPED_SYMBOL.value,
}


def _validate_kind(node_id: NId, kind: object) -> list[str]:
    if not is_stack_graph_kind(kind):
        return [f"Unknown stack graph kind {kind!r} on node {node_id!r}"]
    return []


def _validate_precedence(node_id: NId, precedence: object) -> list[str]:
    if isinstance(precedence, int):
        return []
    return [f"Invalid precedence on node {node_id!r}"]


def _validate_symbol(node_id: NId, kind: str, symbol: object) -> list[str]:
    if kind in _KINDS_WITH_SYMBOL:
        if isinstance(symbol, str) and symbol:
            return []
        return [f"Missing symbol on node {node_id!r}"]
    if symbol is None:
        return []
    return [f"Unexpected symbol on node {node_id!r}"]


def _validate_scope(node_id: NId, kind: str, scope: object) -> list[str]:
    if kind == StackGraphNodeKind.PUSH_SCOPED_SYMBOL.value:
        if isinstance(scope, str) and scope:
            return []
        return [f"Missing scope on node {node_id!r}"]
    if scope is None:
        return []
    return [f"Unexpected scope on node {node_id!r}"]


def _validate_is_exported(node_id: NId, kind: str, is_exported: object) -> list[str]:
    if kind == StackGraphNodeKind.SCOPE.value:
        if isinstance(is_exported, bool):
            return []
        return [f"Missing is_exported on node {node_id!r}"]
    if is_exported is False or is_exported is None:
        return []
    return [f"Unexpected is_exported on node {node_id!r}"]


def validate_stack_graph_node(graph: Graph, node_id: NId) -> list[str]:
    node_data = graph.nodes.get(node_id, {})
    kind = node_data.get(STACK_GRAPH_KIND)
    if kind is None:
        return []

    kind_errors = _validate_kind(node_id, kind)
    if kind_errors:
        return kind_errors

    precedence = node_data.get(STACK_GRAPH_PRECEDENCE, 0)
    symbol = node_data.get(STACK_GRAPH_SYMBOL)
    scope = node_data.get(STACK_GRAPH_SCOPE)
    is_exported = node_data.get(STACK_GRAPH_IS_EXPORTED)

    return [
        *_validate_precedence(node_id, precedence),
        *_validate_symbol(node_id, kind, symbol),
        *_validate_scope(node_id, kind, scope),
        *_validate_is_exported(node_id, kind, is_exported),
    ]


def validate_stack_graph_graph(graph: Graph, *, node_ids: Iterable[NId] | None = None) -> list[str]:
    ids = list(node_ids) if node_ids is not None else list(graph.nodes)
    return [err for node_id in ids for err in validate_stack_graph_node(graph, node_id)]
