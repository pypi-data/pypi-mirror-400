from blends.models import (
    NId,
)
from blends.query import (
    get_nodes_by_path,
    match_ast_group_d,
)
from blends.syntax.builders.class_decl import (
    build_class_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    class_node = args.ast_graph.nodes[args.n_id]
    name_id = class_node["label_field_name"]
    name = node_to_str(args.ast_graph, name_id)
    block_id = class_node.get("label_field_body")
    parameters: list[NId] = []
    annotations = match_ast_group_d(args.ast_graph, args.n_id, "annotation")
    annotation_parameters = get_nodes_by_path(
        args.ast_graph, args.n_id, set(), "annotation", "arguments"
    )
    class_parameters = match_ast_group_d(args.ast_graph, args.n_id, "class_parameters")
    parameters.extend(annotations)
    parameters.extend(annotation_parameters)
    parameters.extend(class_parameters)

    return build_class_node(args, name, block_id, parameters)
