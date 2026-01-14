from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from blends.stack.criteria import (
    is_definition_endpoint,
)

if TYPE_CHECKING:
    from blends.stack.view import (
        StackGraphView,
    )


@dataclass(frozen=True, slots=True)
class PartialPathEdge:
    source_node_index: int
    precedence: int


@dataclass(frozen=True, slots=True)
class DefinitionCandidate:
    definition_node_index: int
    edges: tuple[PartialPathEdge, ...]


def edge_shadows(a: PartialPathEdge, b: PartialPathEdge) -> bool:
    return a.source_node_index == b.source_node_index and a.precedence > b.precedence


def edge_list_shadows(
    a_edges: tuple[PartialPathEdge, ...], b_edges: tuple[PartialPathEdge, ...]
) -> bool:
    if not a_edges or not b_edges:
        return False
    for a_edge, b_edge in zip(a_edges, b_edges, strict=False):
        if a_edge.source_node_index != b_edge.source_node_index:
            return False
        if edge_shadows(a_edge, b_edge):
            return True
    return False


def prune_shadowed_candidates(candidates: list[DefinitionCandidate]) -> list[DefinitionCandidate]:
    kept: list[DefinitionCandidate] = []
    for candidate in sorted(candidates, key=lambda c: c.definition_node_index):
        if any(edge_list_shadows(existing.edges, candidate.edges) for existing in kept):
            continue
        kept = [
            existing for existing in kept if not edge_list_shadows(candidate.edges, existing.edges)
        ]
        kept.append(candidate)
    return kept


def sort_candidates_deterministically(
    candidates: list[DefinitionCandidate],
) -> list[DefinitionCandidate]:
    def sort_key(candidate: DefinitionCandidate) -> tuple[tuple[int, ...], tuple[int, ...], int]:
        edge_sources = tuple(edge.source_node_index for edge in candidate.edges)
        edge_precedences = tuple(-edge.precedence for edge in candidate.edges)
        return (edge_sources, edge_precedences, candidate.definition_node_index)

    return sorted(candidates, key=sort_key)


def select_definition_candidates_from_scope(
    view: StackGraphView, scope_node_index: int, symbol_id: int
) -> list[int]:
    candidates: list[DefinitionCandidate] = []
    for sink_index, edge_precedence in view.outgoing[scope_node_index]:
        if not is_definition_endpoint(view, sink_index):
            continue
        if view.symbol_id_at(sink_index) != symbol_id:
            continue
        candidates.append(
            DefinitionCandidate(
                definition_node_index=sink_index,
                edges=(PartialPathEdge(scope_node_index, edge_precedence),),
            )
        )

    pruned = prune_shadowed_candidates(candidates)
    ordered = sort_candidates_deterministically(pruned)
    return [candidate.definition_node_index for candidate in ordered]
