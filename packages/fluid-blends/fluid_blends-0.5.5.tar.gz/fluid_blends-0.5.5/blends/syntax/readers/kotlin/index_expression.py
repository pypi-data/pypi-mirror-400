from blends.models import (
    NId,
)
from blends.query import adj_ast, match_ast_d
from blends.syntax.builders.element_access import (
    build_element_access_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    expr_id = match_ast_d(graph, args.n_id, "navigation_expression")
    if not expr_id:
        expr_id = adj_ast(graph, args.n_id)[0]

    arguments_id = match_ast_d(graph, args.n_id, "string_literal")
    return build_element_access_node(args, expr_id, arguments_id)
