from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.for_statement import (
    build_for_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    body_id = n_attrs["label_field_body"]
    if graph.nodes[body_id]["label_type"] == "expression_statement":
        body_id = adj_ast(graph, body_id)[0]
    if (
        graph.nodes[body_id]["label_type"] == "parenthesized_expression"
        and (childs := adj_ast(graph, body_id))
        and len(childs) > 1
    ):
        body_id = childs[1]

    initializer_id = n_attrs["label_field_initializer"]
    if graph.nodes[initializer_id]["label_type"] == "expression_statement":
        initializer_id = adj_ast(graph, initializer_id)[0]

    condition_id = n_attrs["label_field_condition"]
    increment_id = n_attrs.get("label_field_increment")

    return build_for_statement_node(args, initializer_id, condition_id, increment_id, body_id)
