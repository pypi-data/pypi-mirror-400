from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.parenthesized_expression import (
    build_parenthesized_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    expr_id = match_ast(args.ast_graph, args.n_id).get("__1__")
    if not expr_id:
        expr_id = adj_ast(args.ast_graph, args.n_id)[0]

    return build_parenthesized_expression_node(args, expr_id)
