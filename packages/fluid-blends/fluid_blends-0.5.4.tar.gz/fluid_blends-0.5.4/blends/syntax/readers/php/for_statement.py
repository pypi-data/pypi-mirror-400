from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.for_statement import (
    build_for_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    c_ids = match_ast(
        graph,
        args.n_id,
        "assignment_expression",
        "binary_expression",
        "update_expression",
    )

    initializer_id = c_ids.get("assignment_expression")
    condition_id = c_ids.get("binary_expression")
    update_id = c_ids.get("update_expression")
    body_id = adj_ast(graph, args.n_id)[-1]

    if graph.nodes[body_id]["label_type"] == "expression_statement":
        body_id = adj_ast(graph, body_id)[0]

    return build_for_statement_node(args, initializer_id, condition_id, update_id, body_id)
