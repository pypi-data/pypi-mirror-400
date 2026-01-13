from blends.models import (
    NId,
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
    expr_id = graph.nodes[args.n_id]["label_field_function"]
    expr_id_child = None
    obj_dict = {}
    if graph.nodes[expr_id]["label_type"] == "field_expression":
        obj_dict = {
            "object_id": graph.nodes[expr_id].get("label_field_value", ""),
        }
        expr = node_to_str(graph, graph.nodes[expr_id]["label_field_field"])
        expr_id_child = graph.nodes[expr_id]["label_field_field"]
    else:
        expr = node_to_str(graph, expr_id)
        obj_dict = {}

    arguments_id = graph.nodes[args.n_id].get("label_field_arguments")
    if arguments_id and graph.nodes[arguments_id]["label_type"] == "block":
        obj_dict["block_id"] = arguments_id
        return build_method_invocation_node(args, expr, expr_id_child, None, obj_dict)

    return build_method_invocation_node(args, expr, expr_id_child, arguments_id, obj_dict)
