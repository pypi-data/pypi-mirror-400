from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.member_access import (
    build_member_access_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)

    relative_n_id = c_ids[0]
    member_n_id = c_ids[-1]

    expression = graph.nodes[member_n_id].get("label_text", "")

    obj_id = match_ast_d(graph, relative_n_id, "self") or member_n_id

    return build_member_access_node(args, "self", expression, obj_id)
