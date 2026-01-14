from blends.models import (
    NId,
)
from blends.syntax.builders.symbol_lookup import (
    build_symbol_lookup_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    label_type = n_attrs.get("label_type")
    if label_type == "wildcard":
        symbol = node_to_str(graph, args.n_id)
    else:
        symbol = args.ast_graph.nodes[args.n_id].get("label_text", "Unknown")
    return build_symbol_lookup_node(args, symbol)
