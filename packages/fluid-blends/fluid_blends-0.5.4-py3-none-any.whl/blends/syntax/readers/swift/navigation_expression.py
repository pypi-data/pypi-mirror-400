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

    expression_id = graph.nodes[args.n_id]["label_field_target"]
    expression = node_to_str(graph, expression_id)

    navigation_suffix = graph.nodes[args.n_id]["label_field_suffix"]
    member_id = graph.nodes[navigation_suffix]["label_field_suffix"]
    member = node_to_str(graph, member_id)

    return build_member_access_node(args, member, expression, expression_id)
