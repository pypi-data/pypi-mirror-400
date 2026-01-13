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
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes

    member_n_id = nodes[args.n_id]["label_field_name"]
    name_n_id = match_ast_d(graph, member_n_id, "name") or member_n_id

    member = nodes[name_n_id].get("label_text", "")

    obj_p_id = nodes[args.n_id].get("label_field_scope")
    expression: str = ""
    if obj_p_id:
        expression = nodes[obj_p_id].get("label_text", "")
        if expression:
            obj_id = obj_p_id
        else:
            obj_c_ids = adj_ast(graph, obj_p_id)
            obj_id = obj_c_ids[0]
            expression = node_to_str(graph, obj_id)

    return build_member_access_node(args, member, expression, obj_id)
