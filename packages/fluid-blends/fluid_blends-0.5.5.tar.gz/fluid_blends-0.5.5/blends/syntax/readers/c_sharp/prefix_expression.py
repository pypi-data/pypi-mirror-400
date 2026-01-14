from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.unary_expression import (
    build_unary_expression_node,
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
    expected_children_for_prefix_expression = 2

    if len(c_ids) == expected_children_for_prefix_expression:
        prefix = node_to_str(graph, c_ids[0])
        expression_id = c_ids[1]
    else:
        expression_id = c_ids[0]
        prefix = "Undefined"

    return build_unary_expression_node(args, prefix, expression_id)
