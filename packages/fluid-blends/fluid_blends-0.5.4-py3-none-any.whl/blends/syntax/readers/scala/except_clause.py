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
    block_id = match_ast_d(graph, args.n_id, "case_block")
    return build_catch_clause_node(args, block_id)
