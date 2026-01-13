from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.member_access import (
    build_member_access_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(args.ast_graph, args.n_id)

    obj_id = c_ids[0]
    expression: str = node_to_str(graph, obj_id)

    member_n_id = c_ids[-1]
    member: str = graph.nodes[member_n_id].get("label_text", "")

    return build_member_access_node(args, member, expression, obj_id)
