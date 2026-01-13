from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.binary_operation import (
    build_binary_operation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    child_ids = adj_ast(graph, args.n_id)
    left_id = None
    operator = ""
    right_id = None
    min_children_for_binary_operation = 2
    if len(child_ids) > min_children_for_binary_operation:
        left_id = child_ids[0]
        operator_id = child_ids[1]
        right_id = child_ids[2]
        operator = graph.nodes[operator_id]["label_text"]
    return build_binary_operation_node(args, operator, left_id, right_id)
