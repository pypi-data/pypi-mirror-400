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
    c_ids = match_ast_group_d(args.ast_graph, args.n_id, "argument") or match_ast_group_d(
        args.ast_graph,
        args.n_id,
        "attribute_argument",
    )

    args_ids = []
    for _id in c_ids:
        if (childs := adj_ast(graph, _id)) and len(childs) == 1:
            args_ids.append(childs[0])
        else:
            args_ids.append(_id)

    return build_argument_list_node(args, iter(args_ids))
