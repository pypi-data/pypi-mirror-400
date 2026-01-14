from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.pair import (
    build_pair_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    key_id = args.ast_graph.nodes[args.n_id]["label_field_key"]
    value_id = args.ast_graph.nodes[args.n_id]["label_field_value"]
    key_child = adj_ast(args.ast_graph, key_id)
    value_child = adj_ast(args.ast_graph, value_id)

    return build_pair_node(args, key_child[0], value_child[0])
