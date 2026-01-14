from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
    match_ast_group_d,
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
        "catch_clause",
        "finally_clause",
        "resource_specification",
    )
    catch_blocks = match_ast_group_d(args.ast_graph, args.n_id, "catch_clause")
    try_block = childs.get("finally_clause")
    resource_specification = childs.get("resource_specification")

    return build_try_statement_node(
        args, block_node, catch_blocks, try_block, resource_specification
    )
