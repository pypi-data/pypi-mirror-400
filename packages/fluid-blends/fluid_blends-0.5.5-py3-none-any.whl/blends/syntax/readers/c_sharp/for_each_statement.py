from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.for_each_statement import (
    build_for_each_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    var_node = n_attrs["label_field_left"]
    iter_item = n_attrs["label_field_right"]

    body_id: NId | None = n_attrs["label_field_body"]

    if body_id and graph.nodes[body_id]["label_type"] == "expression_statement":
        body_id = match_ast(graph, body_id).get("__0__")

    if body_id and graph.nodes[body_id]["label_type"] == "parenthesized_expression":
        body_id = match_ast(graph, body_id).get("__1__")

    return build_for_each_statement_node(args, var_node, iter_item, body_id)
