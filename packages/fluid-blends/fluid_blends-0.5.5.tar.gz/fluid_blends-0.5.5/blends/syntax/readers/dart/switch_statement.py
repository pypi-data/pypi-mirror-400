from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.switch_statement import (
    build_switch_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    body_id = graph.nodes[args.n_id]["label_field_body"]
    value_id = graph.nodes[args.n_id]["label_field_condition"]
    if graph.nodes[value_id]["label_type"] == "parenthesized_expression":
        value_id = match_ast(graph, value_id).get("__1__")
    return build_switch_statement_node(args, body_id, value_id)
