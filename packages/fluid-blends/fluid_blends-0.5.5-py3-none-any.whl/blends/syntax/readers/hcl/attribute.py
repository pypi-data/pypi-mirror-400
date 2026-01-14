from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.pair import (
    build_pair_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    key_id = graph.nodes[args.n_id].get("label_field_key") or match_ast_d(
        graph,
        args.n_id,
        "identifier",
    )
    if not key_id:
        key_id = adj_ast(graph, args.n_id)[0]

    value_id = graph.nodes[args.n_id].get("label_field_val") or match_ast_d(
        graph,
        args.n_id,
        "expression",
    )
    if not value_id:
        value_id = adj_ast(graph, args.n_id)[-1]

    return build_pair_node(args, key_id, value_id)
