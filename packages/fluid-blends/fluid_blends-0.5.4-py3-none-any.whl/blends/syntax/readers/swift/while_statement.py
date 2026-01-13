from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.while_statement import (
    build_while_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    condition_id = n_attrs.get("label_field_condition")
    if not condition_id:
        condition_id = n_attrs.get("label_field_bound_identifier")

    block_id = match_ast_d(graph, args.n_id, "statements")
    if not block_id:
        block_id = adj_ast(graph, args.n_id)[-1]

    return build_while_statement_node(args, block_id, condition_id)
