from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.method_invocation import (
    build_method_invocation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes
    n_attrs = nodes[args.n_id]

    ignored_types = {"(", ",", ")"}

    expr_id = n_attrs["label_field_scope"]
    if nodes[expr_id]["label_type"] == "relative_scope" and (c_ids := adj_ast(graph, expr_id)):
        expr_id = c_ids[0]
    raw_expr = node_to_str(graph, expr_id)
    method_name_n_id = n_attrs["label_field_name"]
    method_name = nodes[method_name_n_id].get("label_text")
    expr = f"{raw_expr}::{method_name}"

    if arguments_id := graph.nodes[args.n_id].get("label_field_arguments"):
        arguments = {
            _id
            for _id in adj_ast(graph, arguments_id)
            if graph.nodes[_id].get("label_type") not in ignored_types
        }
        if not arguments:
            arguments_id = None

    return build_method_invocation_node(args, expr, expr_id, arguments_id, None)
