from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
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
    child_ids = [
        *filter(
            lambda n_id: nodes[n_id].get("label_type") != "line_comment",
            adj_ast(graph, args.n_id),
        ),
    ]
    expected_children_for_member_access = 2
    if (
        len(child_ids) == expected_children_for_member_access
        and graph.nodes[child_ids[1]]["label_type"] == "navigation_suffix"
        and (identifier_id := match_ast(graph, child_ids[1]).get("__1__"))
    ):
        member = node_to_str(graph, identifier_id)
    else:
        member = node_to_str(graph, child_ids[-1])

    expression = node_to_str(graph, child_ids[0])

    return build_member_access_node(args, member, expression, child_ids[0])
