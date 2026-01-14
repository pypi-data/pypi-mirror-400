from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs = match_ast(args.ast_graph, args.n_id, "integer_literal", "simple_identifier")
    expr_id = childs.get("integer_literal") or childs.get("simple_identifier")
    if not expr_id:
        expr_id = adj_ast(args.ast_graph, args.n_id)[0]

    return args.generic(args.fork_n_id(expr_id))
