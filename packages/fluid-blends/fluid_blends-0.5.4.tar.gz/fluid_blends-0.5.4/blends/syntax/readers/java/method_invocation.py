from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
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
    expr_id = graph.nodes[args.n_id]["label_field_name"]

    arguments_id = graph.nodes[args.n_id]["label_field_arguments"]
    if "__0__" not in match_ast(args.ast_graph, arguments_id, "(", ")"):
        arguments_id = None

    expr = node_to_str(graph, expr_id)
    if object_id := graph.nodes[args.n_id].get("label_field_object"):
        obj_dict = {
            "object_id": object_id,
        }
        if graph.nodes[object_id]["label_type"] == "object_creation_expression":
            obj_dict["object"] = node_to_str(graph, graph.nodes[object_id]["label_field_type"])
        return build_method_invocation_node(args, expr, expr_id, arguments_id, obj_dict)

    return build_method_invocation_node(args, expr, expr_id, arguments_id, None)
