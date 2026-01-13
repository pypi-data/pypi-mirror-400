from blends.models import (
    NId,
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
    as_attrs = args.ast_graph.nodes[args.n_id]
    method_name = (
        node_to_str(args.ast_graph, name_id)
        if (name_id := as_attrs.get("label_field_name"))
        else None
    )

    block_id = as_attrs["label_field_body"]
    class_id = as_attrs["label_field_class"]

    return build_method_declaration_node(args, method_name, block_id, {"modifiers_id": [class_id]})
