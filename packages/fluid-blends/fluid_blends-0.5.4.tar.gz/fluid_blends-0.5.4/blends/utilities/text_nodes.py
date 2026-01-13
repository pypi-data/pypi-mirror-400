from collections.abc import (
    Iterator,
)

from blends.models import (
    Graph,
)
from blends.query import (
    adj_ast,
)


def lazy_childs_text(graph: Graph, n_id: str) -> Iterator[str]:
    for c_id in adj_ast(graph, n_id):
        yield from lazy_childs_text(graph, c_id)
    if "label_text" in graph.nodes[n_id]:
        yield graph.nodes[n_id]["label_text"]


def node_to_str(graph: Graph, n_id: str, sep: str = "") -> str:
    return sep.join(lazy_childs_text(graph, n_id))
