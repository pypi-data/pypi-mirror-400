from blends.models import (
    NId,
)
from blends.syntax.builders.binary_operation import (
    build_binary_operation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    left_id = args.ast_graph.nodes[args.n_id]["label_field_left"]
    right_id = args.ast_graph.nodes[args.n_id]["label_field_right"]
    operator_id = args.ast_graph.nodes[args.n_id]["label_field_operator"]
    operator = args.ast_graph.nodes[operator_id]["label_text"]
    return build_binary_operation_node(args, operator, left_id, right_id)
