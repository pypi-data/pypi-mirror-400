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
    n_attrs = graph.nodes[args.n_id]

    name_str = ""
    if name_id := n_attrs.get("label_field_name"):
        name_str = node_to_str(graph, name_id)

    elif val_id := n_attrs.get("label_field_value"):
        name_str = "<<" + node_to_str(graph, val_id)

    block_id = n_attrs.get("label_field_body")

    superclass_name_str = None
    if superclass_id := n_attrs.get("label_field_superclass"):
        superclass_name_str = node_to_str(graph, superclass_id)[1:]

    return build_class_node(args, name_str, block_id, None, superclass_name_str)
