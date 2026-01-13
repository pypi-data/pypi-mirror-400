from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.element_access import (
    build_element_access_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)
    expr_id = c_ids[0] if c_ids else args.n_id
    arguments_id = None

    expected_children_for_subscript_with_arguments = 4
    if len(c_ids) == expected_children_for_subscript_with_arguments:
        arguments_id = c_ids[2]

    return build_element_access_node(args, expr_id, arguments_id)
