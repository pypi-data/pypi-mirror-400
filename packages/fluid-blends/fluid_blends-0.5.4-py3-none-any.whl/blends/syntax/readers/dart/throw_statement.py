from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.throw import (
    build_throw_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    match = match_ast(args.ast_graph, args.n_id, "throw", ";")
    return build_throw_node(args, expression_id=str(match["__0__"]))
