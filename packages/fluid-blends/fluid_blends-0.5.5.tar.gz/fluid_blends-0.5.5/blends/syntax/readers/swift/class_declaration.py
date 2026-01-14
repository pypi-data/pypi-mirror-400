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
    class_node = args.ast_graph.nodes[args.n_id]
    name_id = class_node["label_field_name"]
    name = node_to_str(args.ast_graph, name_id)
    block_id = class_node["label_field_body"]

    return build_class_node(args, name, block_id, None)
