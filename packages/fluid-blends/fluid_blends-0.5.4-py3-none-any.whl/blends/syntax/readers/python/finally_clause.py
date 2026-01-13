from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
)
from blends.syntax.builders.finally_clause import (
    build_finally_clause_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    block = match_ast_d(graph, args.n_id, "block")
    return build_finally_clause_node(args, block)
