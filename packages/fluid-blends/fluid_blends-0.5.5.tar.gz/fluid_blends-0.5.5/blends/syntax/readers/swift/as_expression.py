from blends.models import (
    NId,
)
from blends.syntax.builders.binary_operation import build_binary_operation_node
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    left_id = args.ast_graph.nodes[args.n_id]["label_field_expr"]
    right_id = args.ast_graph.nodes[args.n_id]["label_field_type"]
    operator = "as_expression"
    return build_binary_operation_node(args, operator, left_id, right_id)
