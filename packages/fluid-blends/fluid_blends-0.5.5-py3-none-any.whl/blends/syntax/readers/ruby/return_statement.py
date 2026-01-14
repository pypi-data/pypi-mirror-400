from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
)
from blends.syntax.builders.return_statement import (
    build_return_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    argument_list_id = match_ast_d(graph, args.n_id, "argument_list")

    return build_return_node(args, argument_list_id)
