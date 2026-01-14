from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.using_statement import (
    build_using_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    block_id = graph.nodes[args.n_id]["label_field_body"]
    if graph.nodes[block_id]["label_type"] == "expression_statement":
        block_id = adj_ast(graph, block_id)[0]

    children = match_ast(graph, args.n_id, "variable_declaration")
    declaration_id = children.get("variable_declaration")
    return build_using_statement_node(args, block_id, declaration_id)
