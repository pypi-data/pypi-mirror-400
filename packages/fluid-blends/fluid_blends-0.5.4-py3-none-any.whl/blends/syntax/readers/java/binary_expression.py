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
    left_id = args.ast_graph.nodes[args.n_id]["label_field_left"]
    if graph.nodes[left_id]["label_type"] == "parenthesized_expression":
        left_id = match_ast(graph, left_id)["__1__"]
    right_id = args.ast_graph.nodes[args.n_id]["label_field_right"]
    if graph.nodes[right_id]["label_type"] == "parenthesized_expression":
        right_id = match_ast(graph, right_id)["__1__"]
    operator_id = args.ast_graph.nodes[args.n_id]["label_field_operator"]
    operator = args.ast_graph.nodes[operator_id]["label_text"]
    return build_binary_operation_node(args, operator, left_id, right_id)
