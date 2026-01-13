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
    block_id = match_ast_d(args.ast_graph, args.n_id, "statement_block")
    return build_finally_clause_node(args, block_id)
