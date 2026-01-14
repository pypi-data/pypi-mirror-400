from blends.models import (
    NId,
)
from blends.query import (
    get_nodes_by_path,
    match_ast,
)
from blends.syntax.builders.try_statement import (
    build_try_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    block_node = args.ast_graph.nodes[args.n_id]["label_field_body"]
    childs = match_ast(
        args.ast_graph,
        args.n_id,
        "finally_clause",
    )
    catch_blocks = get_nodes_by_path(
        args.ast_graph,
        args.n_id,
        set(),
        "catch_clause",
    )
    try_block = childs.get("finally_clause")
    return build_try_statement_node(args, block_node, catch_blocks, try_block, None)
