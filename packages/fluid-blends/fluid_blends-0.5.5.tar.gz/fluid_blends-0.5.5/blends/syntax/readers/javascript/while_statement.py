from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.while_statement import (
    build_while_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    match_childs = match_ast(
        args.ast_graph,
        args.n_id,
        "parenthesized_expression",
        "statement_block",
    )
    block_id = match_childs.get("statement_block")
    if not block_id:
        block_id = adj_ast(graph, args.n_id)[-1]

    if block_id and graph.nodes[block_id]["label_type"] == "expression_statement":
        block_id = adj_ast(graph, block_id)[0]

    conditional_id = match_childs.get("parenthesized_expression")

    return build_while_statement_node(args, block_id, conditional_id)
