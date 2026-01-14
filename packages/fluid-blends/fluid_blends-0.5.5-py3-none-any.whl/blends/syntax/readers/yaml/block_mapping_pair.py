from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.pair import (
    build_pair_node,
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
    key_id = n_attrs.get("label_field_key")
    value_id = n_attrs.get("label_field_value")
    if value_id and key_id:
        if graph.nodes[value_id]["label_type"] == "block_node":
            value_id = adj_ast(graph, value_id)[-1]
        return build_pair_node(args, key_id, value_id)

    symbol = node_to_str(graph, args.n_id)
    return build_symbol_lookup_node(args, symbol)
