from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.if_statement import (
    build_if_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]

    condition_id = n_attrs["label_field_condition"]
    if graph.nodes[condition_id]["label_type"] == "parenthesized_expression":
        condition_id = match_ast(graph, condition_id).get("__1__")

    true_id = n_attrs["label_field_consequence"]
    if graph.nodes[true_id]["label_type"] == "expression_statement":
        true_id = adj_ast(graph, true_id)[0]

    false_id = n_attrs.get("label_field_alternative")
    if false_id and graph.nodes[false_id]["label_type"] == "expression_statement":
        false_id = adj_ast(graph, false_id)[0]

    return build_if_node(args, condition_id, true_id, false_id)
