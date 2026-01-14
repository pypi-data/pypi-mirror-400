from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.reserved_word import (
    build_reserved_word_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs = match_ast(args.ast_graph, args.n_id)
    if c_id := childs.get("__1__"):
        expression = f"PackageName {node_to_str(args.ast_graph, c_id)}"
        if metadata_node := args.syntax_graph.nodes.get("0"):
            metadata_node["package"] = node_to_str(args.ast_graph, c_id)
    else:
        expression = "PackageName Unnamed"
    return build_reserved_word_node(args, expression)
