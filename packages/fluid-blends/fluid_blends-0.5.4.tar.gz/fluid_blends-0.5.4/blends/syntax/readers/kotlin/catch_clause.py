from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
)
from blends.syntax.builders.catch_clause import (
    build_catch_clause_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    block = match_ast_d(graph, args.n_id, "statements")
    param_id = match_ast_d(graph, args.n_id, "identifier")
    return build_catch_clause_node(args, block, param_id)
