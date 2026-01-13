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
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)
    expected_children_for_infix_expression = 3
    if len(c_ids) == expected_children_for_infix_expression:
        right_id = c_ids[0]
        operator = node_to_str(graph, c_ids[1])
        left_id = c_ids[2]
    else:
        right_id = None
        operator = "UndefinedInfix"
        left_id = None

    return build_binary_operation_node(
        args,
        operator,
        left_id,
        right_id,
    )
