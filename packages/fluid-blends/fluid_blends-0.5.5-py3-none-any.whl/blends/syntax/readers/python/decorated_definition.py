from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
    match_ast_group_d,
)
from blends.syntax.builders.class_decl import (
    build_class_node,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    def_id = n_attrs["label_field_definition"]
    modifiers_list = match_ast_group_d(graph, args.n_id, "decorator")

    if graph.nodes[def_id]["label_type"] == "function_definition":
        method_node = graph.nodes[def_id]
        name_id = method_node["label_field_name"]
        name = node_to_str(graph, name_id)
        block_id = method_node["label_field_body"]

        parameters_id = method_node["label_field_parameters"]
        parameters_list = []
        if "__0__" in match_ast(graph, parameters_id, "(", ")"):
            parameters_list = [parameters_id]

        children_nid = {
            "parameters_id": parameters_list,
            "modifiers_id": modifiers_list,
        }

        return build_method_declaration_node(args, name, block_id, children_nid)

    class_node = graph.nodes[def_id]
    name_id = class_node["label_field_name"]
    name = node_to_str(graph, name_id)
    block_id = class_node["label_field_body"]

    return build_class_node(args, name, block_id, modifiers_list)
