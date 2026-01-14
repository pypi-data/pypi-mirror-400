from blends.models import (
    NId,
)
from blends.query import (
    get_node_by_path,
    match_ast_group,
    match_ast_group_d,
)
from blends.syntax.builders.class_decl import (
    build_class_node,
)
from blends.syntax.metadata.java import (
    add_class_to_metadata,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    class_node = args.ast_graph.nodes[args.n_id]
    name_id = class_node["label_field_name"]
    block_id = class_node["label_field_body"]
    name = node_to_str(graph, name_id)

    inherited_class: str | None = None
    if extends_id := get_node_by_path(graph, args.n_id, "superclass", "type_identifier"):
        inherited_class = graph.nodes[extends_id].get("label_text", None)

    if (
        implements_id := get_node_by_path(
            graph,
            args.n_id,
            "super_interfaces",
            "type_list",
            "type_identifier",
        )
    ) and (implements_value := graph.nodes[implements_id].get("label_text")):
        if inherited_class is not None:
            inherited_class = f"{inherited_class},{implements_value}"
        else:
            inherited_class = implements_value

    if args.syntax_graph.nodes.get("0"):
        add_class_to_metadata(args, name)

    modifiers_id: NId | None = None
    if modifiers := match_ast_group_d(graph, args.n_id, "modifiers"):
        annotation_ids_raw = match_ast_group(graph, modifiers[0], "annotation", "marker_annotation")
        annotation_ids = annotation_ids_raw["annotation"] + annotation_ids_raw["marker_annotation"]
        if len(annotation_ids) > 0:
            modifiers_id = modifiers[0]

    return build_class_node(
        args,
        name,
        block_id,
        None,
        inherited_class,
        modifiers_id,
    )
