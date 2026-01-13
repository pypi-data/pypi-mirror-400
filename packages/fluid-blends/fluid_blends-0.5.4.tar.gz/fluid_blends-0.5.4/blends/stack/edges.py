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
    graph.add_edge(graph_edge.source, graph_edge.sink, precedence=graph_edge.precedence)
