from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
    match_ast_group_d,
)
from blends.syntax.builders.try_statement import (
    build_try_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    block_id = match_ast_d(graph, args.n_id, "block")
    if not block_id:
        block_id = adj_ast(graph, args.n_id)[-1]

    catch_blocks = match_ast_group_d(args.ast_graph, args.n_id, "catch_block")
    finally_block = match_ast_d(graph, args.n_id, "label_field_finally_block")

    return build_try_statement_node(args, block_id, catch_blocks, finally_block, None)
