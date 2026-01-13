from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.symbol_lookup import (
    build_symbol_lookup_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    var_name = ""
    if identifiers := match_ast_group_d(graph, args.n_id, "identifier"):
        var_name = ".".join(
            graph.nodes[_id]["label_text"]
            for _id in identifiers
            if "label_text" in graph.nodes[_id]
        )
    return build_symbol_lookup_node(args, var_name)
