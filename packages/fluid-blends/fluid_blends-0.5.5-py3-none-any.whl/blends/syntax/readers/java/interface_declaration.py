from blends.models import (
    NId,
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
    graph = args.ast_graph
    name_id = graph.nodes[args.n_id]["label_field_name"]
    name = node_to_str(graph, name_id)
    body_id = graph.nodes[args.n_id]["label_field_body"]
    return build_class_node(args, name, body_id, None)
