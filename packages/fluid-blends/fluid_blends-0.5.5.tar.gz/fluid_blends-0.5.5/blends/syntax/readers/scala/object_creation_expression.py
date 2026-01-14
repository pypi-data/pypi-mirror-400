from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
)
from blends.syntax.builders.object_creation import (
    build_object_creation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    node_attr = args.ast_graph.nodes[args.n_id]

    if name_id := node_attr.get("label_field_name"):
        name = graph.nodes[name_id].get("label_text", "")
        arguments_id = node_attr.get("label_field_body")
    elif name_id := match_ast_d(graph, args.n_id, "type_identifier"):
        name = graph.nodes[name_id].get("label_text", "")
        arguments_id = node_attr.get("label_field_arguments")
    else:
        name = node_to_str(args.ast_graph, args.n_id)
        arguments_id = None

    return build_object_creation_node(args, name, arguments_id, None)
