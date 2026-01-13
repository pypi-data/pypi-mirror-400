from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
    match_ast_group,
    match_ast_group_d,
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

    name_id = graph.nodes[args.n_id].get("label_field_name")
    name = node_to_str(graph, name_id) if name_id else None

    block_id = match_ast_d(graph, args.n_id, "function_body")
    if not block_id:
        block_id = match_ast_d(graph, args.n_id, "statements")

    children_nid: dict[str, list[NId]] = {}

    parameters_id = graph[args.n_id].get("label_field_parameters") or match_ast_d(
        graph, args.n_id, "function_value_parameters"
    )

    if parameters_id:
        children_nid["parameters_id"] = [str(parameters_id)]

    modifiers_id = match_ast_group_d(graph, args.n_id, "modifiers")
    if modifiers_id:
        first_modifier_id = modifiers_id[0]
        annotation_ids_raw = match_ast_group(
            graph,
            first_modifier_id,
            "annotation",
        )
        annotation_ids = annotation_ids_raw.get("annotation", [])
        if len(annotation_ids) == 0:
            modifiers_id = []
    if modifiers_id:
        children_nid["modifiers_id"] = modifiers_id

    return build_method_declaration_node(args, name, block_id, children_nid)
