from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
    match_ast_group_d,
)
from blends.syntax.builders.if_statement import (
    build_if_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    condition_id = (
        n_attrs.get("label_field_condition")
        or match_ast_d(graph, args.n_id, "simple_identifier")
        or match_ast_d(graph, args.n_id, "call_expression")
        or adj_ast(graph, args.n_id)[0]
    )
    initializer_id = n_attrs.get("label_field_bound_identifier")
    if (
        condition_id is not None
        and graph.nodes[condition_id]["label_type"] == "value_binding_pattern"
        and (
            (try_id := match_ast_d(graph, args.n_id, "try_expression"))
            or (call_expr := match_ast_d(graph, args.n_id, "call_expression"))
        )
    ):
        condition_id = try_id or call_expr

    statements = match_ast_group_d(graph, args.n_id, "statements")

    true_id = None
    false_id = None

    expected_statements_for_if_with_else = 2
    if len(statements) == expected_statements_for_if_with_else:
        true_id = statements[0]
        false_id = statements[1]
    elif len(statements) == 1:
        true_id = statements[0]

    if false_statement := match_ast_d(graph, args.n_id, "if_statement"):
        false_id = false_statement

    return build_if_node(
        args, condition_id, true_id, false_id, initializer_id if initializer_id else None
    )
