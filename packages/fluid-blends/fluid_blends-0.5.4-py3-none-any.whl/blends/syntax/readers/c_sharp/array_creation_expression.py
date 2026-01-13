from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.array_node import (
    build_array_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    children = match_ast_group_d(args.ast_graph, args.n_id, "initializer_expression")
    return build_array_node(args, iter(children))
