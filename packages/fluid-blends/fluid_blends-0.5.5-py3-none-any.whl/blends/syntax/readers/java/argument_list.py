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
    _, *c_add, _ = adj_ast(graph, args.n_id)  # do not consider ( )
    c_ids = set(match_ast_group_d(graph, args.n_id, "identifier"))
    c_ids.update(filter(None, c_add))

    return build_argument_list_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"] != ","),
    )
