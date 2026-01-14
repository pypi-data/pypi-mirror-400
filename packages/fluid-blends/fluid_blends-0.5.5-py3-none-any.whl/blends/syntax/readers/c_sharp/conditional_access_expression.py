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
    expression_id = graph.nodes[args.n_id]["label_field_condition"]
    expression = node_to_str(graph, expression_id)
    member_id = (
        match_ast_d(graph, args.n_id, "member_binding_expression")
        or match_ast_d(graph, args.n_id, "element_binding_expression")
        or adj_ast(graph, args.n_id)[-1]
    )
    member = node_to_str(graph, member_id).strip(".")
    return build_member_access_node(args, member, expression, expression_id)
