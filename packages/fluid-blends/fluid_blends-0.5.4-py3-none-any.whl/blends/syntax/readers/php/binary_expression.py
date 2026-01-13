from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.binary_operation import (
    build_binary_operation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes
    operator_id = nodes[args.n_id]["label_field_operator"]
    operator = nodes[operator_id]["label_text"]
    left_id = nodes[args.n_id]["label_field_left"]
    right_id = nodes[args.n_id]["label_field_right"]

    if nodes[left_id].get("label_type") == "parenthesized_expression":
        c_ids = match_ast(graph, left_id)
        left_id = c_ids.get("__1__")
    if nodes[right_id].get("label_type") == "parenthesized_expression":
        c_ids = match_ast(graph, right_id)
        right_id = c_ids.get("__1__")

    return build_binary_operation_node(args, operator, left_id, right_id)
