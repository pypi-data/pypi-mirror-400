from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.argument_list import (
    build_argument_list_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    c_ids = match_ast_group_d(args.ast_graph, args.n_id, "argument")
    return build_argument_list_node(args, iter(c_ids))
