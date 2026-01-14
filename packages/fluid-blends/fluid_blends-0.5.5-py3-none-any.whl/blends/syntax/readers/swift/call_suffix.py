from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_group_d,
)
from blends.syntax.builders.argument_list import (
    build_argument_list_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    arg_ids = []

    for _id in adj_ast(graph, args.n_id):
        if graph.nodes[_id]["label_type"] == "value_arguments":
            arg_ids.extend(match_ast_group_d(graph, _id, "value_argument"))
        else:
            arg_ids.append(_id)

    return build_argument_list_node(args, iter(arg_ids))
