from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.return_statement import (
    build_return_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs = match_ast(args.ast_graph, args.n_id, "return", ";")
    if val_id := childs.get("__0__"):
        return build_return_node(args, val_id)
    return build_return_node(args, None)
