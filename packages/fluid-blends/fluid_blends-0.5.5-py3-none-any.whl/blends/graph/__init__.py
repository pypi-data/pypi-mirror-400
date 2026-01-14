from pathlib import Path
from typing import NamedTuple

from blends.ast.build_graph import get_ast_from_content
from blends.content.content import get_content_by_path
from blends.models import Graph
from blends.syntax.build_graph import get_syntax_graph


class GraphPair(NamedTuple):
    ast_graph: Graph | None
    syntax_graph: Graph | None


def get_graphs_from_path(path: Path) -> GraphPair:
    content = get_content_by_path(path)
    if content is None:
        return GraphPair(ast_graph=None, syntax_graph=None)

    ast_graph = get_ast_from_content(content)
    if ast_graph is None:
        return GraphPair(ast_graph=None, syntax_graph=None)

    syntax_graph = get_syntax_graph(ast_graph, content)
    if syntax_graph is None:
        return GraphPair(ast_graph=ast_graph, syntax_graph=None)

    return GraphPair(ast_graph=ast_graph, syntax_graph=syntax_graph)


__all__ = ["GraphPair", "get_graphs_from_path"]
