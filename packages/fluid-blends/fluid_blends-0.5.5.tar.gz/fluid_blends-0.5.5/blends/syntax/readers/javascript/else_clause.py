from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.else_clause import (
    build_else_clause_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    childs = match_ast(graph, args.n_id, "else")
    body_id = childs.get("__0__")

    if body_id and graph.nodes[body_id]["label_type"] == "expression_statement":
        body_id = match_ast(graph, body_id).get("__0__")

    if body_id and graph.nodes[body_id]["label_type"] == "parenthesized_expression":
        body_id = match_ast(graph, body_id).get("__1__")

    if not body_id:
        body_id = adj_ast(graph, args.n_id)[-1]

    return build_else_clause_node(args, body_id)
