from blends.models import (
    NId,
)
from blends.query import (
    pred_ast,
)
from blends.syntax.builders.named_argument import (
    build_named_argument_node,
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
    key_id = args.ast_graph.nodes[args.n_id]["label_field_key"]
    if not (value_id := args.ast_graph.nodes[args.n_id].get("label_field_value")):
        symbol = node_to_str(args.ast_graph, key_id)
        return build_symbol_lookup_node(args, symbol)

    parent = pred_ast(args.ast_graph, args.n_id)
    if args.ast_graph.nodes[parent[0]]["label_type"] == "argument_list":
        arg_name = node_to_str(args.ast_graph, key_id)
        return build_named_argument_node(args, arg_name, value_id)

    return build_pair_node(args, key_id, value_id)
