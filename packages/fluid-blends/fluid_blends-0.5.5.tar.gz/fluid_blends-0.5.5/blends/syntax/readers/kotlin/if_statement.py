from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.if_statement import (
    build_if_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    child_ids = adj_ast(graph, args.n_id)
    condition_id = child_ids[2]
    if (
        graph.nodes[condition_id]["label_type"] == "parenthesized_expression"
        and (childs := adj_ast(graph, condition_id))
        and len(childs) > 1
    ):
        condition_id = childs[1]

    true_id = child_ids[4]
    false_id = None
    expected_children_for_if_with_else = 7
    if len(child_ids) == expected_children_for_if_with_else:
        false_id = child_ids[6]
    return build_if_node(args, condition_id, true_id, false_id)
