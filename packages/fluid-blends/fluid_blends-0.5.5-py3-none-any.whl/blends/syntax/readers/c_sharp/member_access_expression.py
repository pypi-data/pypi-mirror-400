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
    member_id = args.ast_graph.nodes[args.n_id]["label_field_name"]
    expression_id = args.ast_graph.nodes[args.n_id]["label_field_expression"]
    member = node_to_str(args.ast_graph, member_id)
    expression = node_to_str(args.ast_graph, expression_id)
    return build_member_access_node(args, member, expression, expression_id)
