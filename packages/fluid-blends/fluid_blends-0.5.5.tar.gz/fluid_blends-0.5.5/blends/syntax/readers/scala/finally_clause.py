from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.finally_clause import (
    build_finally_clause_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs = match_ast(args.ast_graph, args.n_id, "block")
    finally_block = childs.get("block")
    return build_finally_clause_node(args, finally_block)
