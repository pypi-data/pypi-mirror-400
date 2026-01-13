from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from blends.models import (
        Graph,
        NId,
    )

ROOT_NID: NId = "__stack_graph_root__"
JUMP_TO_NID: NId = "__stack_graph_jump_to__"


class Degree(IntEnum):
    ZERO = 0
    ONE = 1
    MULTIPLE = 2


def _nid_sort_key(n_id: NId) -> tuple[int, int | str]:
    if n_id.isdecimal():
        return (0, int(n_id))
    return (1, n_id)


def _resolve_file_path(graph: Graph, path: str | None) -> str:
    if path is not None:
        return path
    metadata = graph.nodes.get("0", {})
    node_path = metadata.get("path")
    return node_path if isinstance(node_path, str) else ""


def _collect_stack_graph_node_ids(graph: Graph) -> list[NId]:
    return [
        node_id
        for node_id in graph.nodes(data=True)
        if graph.nodes[node_id].get(STACK_GRAPH_KIND) is not None
    ]


def _build_node_index_maps(stack_node_ids: list[NId]) -> tuple[dict[NId, int], list[NId]]:
    nid_to_index: dict[NId, int] = {ROOT_NID: 0, JUMP_TO_NID: 1}
    index_to_nid: list[NId] = [ROOT_NID, JUMP_TO_NID]
    for node_id in stack_node_ids:
        if node_id in nid_to_index:
            continue
        nid_to_index[node_id] = len(index_to_nid)
        index_to_nid.append(node_id)
    return nid_to_index, index_to_nid


def _extract_node_semantics(
    graph: Graph,
    *,
    stack_node_ids: list[NId],
    nid_to_index: dict[NId, int],
    symbols: SymbolInterner,
    node_count: int,
) -> tuple[list[str | None], list[int | None], list[int | None], list[int], set[int]]:
    node_kind: list[str | None] = [None] * node_count
    node_symbol_id: list[int | None] = [None] * node_count
    node_scope_index: list[int | None] = [None] * node_count
    node_precedence: list[int] = [0] * node_count
    exported_scopes: set[int] = set()

    node_kind[nid_to_index[ROOT_NID]] = StackGraphNodeKind.ROOT.value
    node_kind[nid_to_index[JUMP_TO_NID]] = StackGraphNodeKind.JUMP_TO.value

    for node_id in stack_node_ids:
        node_index = nid_to_index[node_id]
        attrs = graph.nodes.get(node_id, {})

        kind = attrs.get(STACK_GRAPH_KIND)
        if isinstance(kind, str):
            node_kind[node_index] = kind

        symbol = attrs.get(STACK_GRAPH_SYMBOL)
        if isinstance(symbol, str) and symbol:
            node_symbol_id[node_index] = symbols.intern(symbol)

        scope = attrs.get(STACK_GRAPH_SCOPE)
        if isinstance(scope, str):
            node_scope_index[node_index] = nid_to_index.get(scope)

        precedence = attrs.get(STACK_GRAPH_PRECEDENCE, 0)
        node_precedence[node_index] = precedence if isinstance(precedence, int) else 0

        is_exported = attrs.get(STACK_GRAPH_IS_EXPORTED)
        if is_exported is True:
            exported_scopes.add(node_index)

    return node_kind, node_symbol_id, node_scope_index, node_precedence, exported_scopes


def _extract_and_normalize_outgoing(
    graph: Graph,
    *,
    stack_node_ids: list[NId],
    nid_to_index: dict[NId, int],
    node_count: int,
) -> list[list[tuple[int, int]]]:
    outgoing: list[list[tuple[int, int]]] = [[] for _ in range(node_count)]
    stack_node_id_set = set(stack_node_ids)
    for source_id, sink_id, edge_attrs in graph.edges(data=True):
        if source_id not in stack_node_id_set or sink_id not in stack_node_id_set:
            continue
        source_index = nid_to_index[source_id]
        sink_index = nid_to_index[sink_id]
        precedence = edge_attrs.get("precedence", 0)
        outgoing[source_index].append(
            (
                sink_index,
                precedence if isinstance(precedence, int) else 0,
            )
        )

    normalized_outgoing: list[list[tuple[int, int]]] = [[] for _ in range(node_count)]
    for source_index, edges in enumerate(outgoing):
        if not edges:
            continue
        edges.sort(key=lambda item: (item[0], item[1]))
        normalized_outgoing[source_index] = edges

    return normalized_outgoing


def _compute_incoming_degree(
    outgoing: list[list[tuple[int, int]]], node_count: int
) -> list[Degree]:
    incoming_counts: list[int] = [0] * node_count
    for edges in outgoing:
        for sink_index, _ in edges:
            incoming_counts[sink_index] += 1
    return [
        Degree.ZERO if count == 0 else Degree.ONE if count == 1 else Degree.MULTIPLE
        for count in incoming_counts
    ]


def _build_file_maps(
    file_path: str, *, stack_node_ids: list[NId], nid_to_index: dict[NId, int], node_count: int
) -> tuple[dict[str, frozenset[int]], list[str]]:
    real_node_indices = frozenset(nid_to_index[node_id] for node_id in stack_node_ids)
    file_to_nodes = {file_path: real_node_indices}
    node_to_file = [file_path if index in real_node_indices else "" for index in range(node_count)]
    return file_to_nodes, node_to_file


@dataclass(slots=True)
class SymbolInterner:
    symbol_to_id: dict[str, int]
    id_to_symbol: list[str]

    def intern(self, symbol: str) -> int:
        symbol_id = self.symbol_to_id.get(symbol)
        if symbol_id is not None:
            return symbol_id
        symbol_id = len(self.id_to_symbol)
        self.symbol_to_id[symbol] = symbol_id
        self.id_to_symbol.append(symbol)
        return symbol_id

    def lookup(self, symbol_id: int) -> str:
        return self.id_to_symbol[symbol_id]


@dataclass(frozen=True, slots=True)
class StackGraphView:
    file_path: str
    nid_to_index: dict[NId, int]
    index_to_nid: list[NId]
    symbols: SymbolInterner
    node_kind: list[str | None]
    node_symbol_id: list[int | None]
    node_scope_index: list[int | None]
    node_precedence: list[int]
    outgoing: list[list[tuple[int, int]]]
    incoming_degree: list[Degree]
    exported_scopes: set[int]
    file_to_nodes: dict[str, frozenset[int]]
    node_to_file: list[str]

    @classmethod
    def from_syntax_graph(cls, graph: Graph, *, path: str | None = None) -> StackGraphView:
        file_path = _resolve_file_path(graph, path)

        stack_node_ids = sorted(_collect_stack_graph_node_ids(graph), key=_nid_sort_key)
        nid_to_index, index_to_nid = _build_node_index_maps(stack_node_ids)

        symbols = SymbolInterner(symbol_to_id={}, id_to_symbol=[])

        node_count = len(index_to_nid)
        node_kind, node_symbol_id, node_scope_index, node_precedence, exported_scopes = (
            _extract_node_semantics(
                graph,
                stack_node_ids=stack_node_ids,
                nid_to_index=nid_to_index,
                symbols=symbols,
                node_count=node_count,
            )
        )
        outgoing = _extract_and_normalize_outgoing(
            graph,
            stack_node_ids=stack_node_ids,
            nid_to_index=nid_to_index,
            node_count=node_count,
        )
        incoming_degree = _compute_incoming_degree(outgoing, node_count)
        file_to_nodes, node_to_file = _build_file_maps(
            file_path,
            stack_node_ids=stack_node_ids,
            nid_to_index=nid_to_index,
            node_count=node_count,
        )

        return cls(
            file_path=file_path,
            nid_to_index=nid_to_index,
            index_to_nid=index_to_nid,
            symbols=symbols,
            node_kind=node_kind,
            node_symbol_id=node_symbol_id,
            node_scope_index=node_scope_index,
            node_precedence=node_precedence,
            outgoing=outgoing,
            incoming_degree=incoming_degree,
            exported_scopes=exported_scopes,
            file_to_nodes=file_to_nodes,
            node_to_file=node_to_file,
        )

    def kind_at(self, node_index: int) -> str:
        if node_index == 0:
            return StackGraphNodeKind.ROOT.value
        if node_index == 1:
            return StackGraphNodeKind.JUMP_TO.value
        kind = self.node_kind[node_index]
        return kind if isinstance(kind, str) else ""

    def symbol_id_at(self, node_index: int) -> int | None:
        if node_index in {0, 1}:
            return None
        return self.node_symbol_id[node_index]

    def scope_index_at(self, node_index: int) -> int | None:
        if node_index in {0, 1}:
            return None
        return self.node_scope_index[node_index]
