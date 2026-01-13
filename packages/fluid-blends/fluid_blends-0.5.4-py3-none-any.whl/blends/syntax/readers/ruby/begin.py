from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
    match_ast_group_d,
)
from blends.syntax.builders.reserved_word import (
    build_reserved_word_node,
)
from blends.syntax.builders.try_statement import (
    build_try_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    childs = match_ast(graph, args.n_id, "call", "assignment")
    block_node = childs.get("assignment")
    if not block_node:
        direct_childs = adj_ast(graph, args.n_id)
        min_children_for_begin_block = 2
        if len(direct_childs) < min_children_for_begin_block:
            return build_reserved_word_node(args, "begin")
        block_node = direct_childs[1]

    try_block_id = childs.get("call")
    catch_blocks = match_ast_group_d(graph, args.n_id, "rescue")
    return build_try_statement_node(args, block_node, catch_blocks, try_block_id, None)
