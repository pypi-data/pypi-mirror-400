from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    expr_id = adj_ast(args.ast_graph, args.n_id)[0]
    return args.generic(args.fork_n_id(expr_id))
