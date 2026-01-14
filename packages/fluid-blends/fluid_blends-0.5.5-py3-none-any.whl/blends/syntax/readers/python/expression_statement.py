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
    graph = args.ast_graph
    childs = match_ast(graph, args.n_id, "del", "global")
    expr_id = childs.get("__0__")
    if not expr_id:
        expr_id = adj_ast(graph, args.n_id)[0]
    return args.generic(args.fork_n_id(expr_id))
