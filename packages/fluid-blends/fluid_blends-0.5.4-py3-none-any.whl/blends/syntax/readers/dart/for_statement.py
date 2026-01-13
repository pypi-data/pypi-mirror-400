from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.for_each_statement import (
    build_for_each_statement_node,
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

    var_node = n_attrs.get("label_field_name")
    iterable_item = n_attrs.get("label_field_value")
    if var_node and iterable_item:
        return build_for_each_statement_node(args, var_node, iterable_item, body_id)

    init_id = n_attrs.get("label_field_init")
    condition_id = n_attrs.get("label_field_condition")
    increment_id = n_attrs.get("label_field_update")
    return build_for_statement_node(args, init_id, condition_id, increment_id, body_id)
