from dataclasses import dataclass

from blends.models import (
    Graph,
    NId,
)


@dataclass(frozen=True, slots=True)
class Edge:
    source: NId
    sink: NId
    precedence: int = 0


def add_edge(graph: Graph, graph_edge: Edge) -> None:
    source = graph_edge.source
    sink = graph_edge.sink
    precedence = graph_edge.precedence if isinstance(graph_edge.precedence, int) else 0
    if graph.has_edge(source, sink):
        existing_data = graph.get_edge_data(source, sink, default={})
        existing_precedence = existing_data.get("precedence", 0)
        if isinstance(existing_precedence, int):
            precedence = max(existing_precedence, precedence)
    graph.add_edge(source, sink, precedence=precedence)
