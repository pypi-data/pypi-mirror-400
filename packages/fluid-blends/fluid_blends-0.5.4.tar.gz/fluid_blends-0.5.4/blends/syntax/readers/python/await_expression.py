from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.await_expression import (
    build_await_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs = match_ast(args.ast_graph, args.n_id, "await")
    expr_id = childs.get("__0__")
    if not expr_id:
        expr_id = adj_ast(args.ast_graph, args.n_id)[-1]
    return build_await_expression_node(args, expr_id)
