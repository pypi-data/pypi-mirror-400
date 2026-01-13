from blends.models import (
    NId,
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
    expression_id = graph.nodes[args.n_id]["label_field_object"]
    expression = node_to_str(graph, expression_id) if expression_id else "DefaultObject"

    member_id = graph.nodes[args.n_id].get("label_field_property", None)
    member = node_to_str(graph, member_id) if member_id else "DefaultMember"
    return build_member_access_node(args, member, expression, expression_id)
