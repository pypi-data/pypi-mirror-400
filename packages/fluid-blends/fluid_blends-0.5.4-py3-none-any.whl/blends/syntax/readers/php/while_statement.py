from blends.models import (
    NId,
)
from blends.query import (
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
    n_attrs = graph.nodes[args.n_id]
    condition_id = n_attrs["label_field_condition"]
    block = n_attrs["label_field_body"]

    if graph.nodes[condition_id].get("label_type") == "parenthesized_expression":
        c_ids = match_ast(graph, condition_id)
        condition_id = c_ids.get("__1__")

    return build_while_statement_node(args, block, condition_id)
