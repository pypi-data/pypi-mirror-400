from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
    match_ast_group,
    match_ast_group_d,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.metadata.java import (
    add_method_to_metadata,
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
    name_id = n_attrs["label_field_name"]
    name = node_to_str(graph, name_id)

    block_id = n_attrs.get("label_field_body")

    parameters_id = n_attrs["label_field_parameters"]
    if "__0__" not in match_ast(graph, parameters_id, "(", ")"):
        parameters_list = []
    else:
        parameters_list = [parameters_id]

    if modifiers_id := match_ast_group_d(graph, args.n_id, "modifiers"):
        annotation_ids_raw = match_ast_group(
            graph,
            modifiers_id[0],
            "annotation",
            "marker_annotation",
        )
        annotation_ids = annotation_ids_raw["annotation"] + annotation_ids_raw["marker_annotation"]

        if len(annotation_ids) == 0:
            modifiers_id = []

    children_nid = {
        "modifiers_id": modifiers_id,
        "parameters_id": parameters_list,
    }

    if args.syntax_graph.nodes.get("0"):
        add_method_to_metadata(args, name)

    return build_method_declaration_node(args, name, block_id, children_nid)
