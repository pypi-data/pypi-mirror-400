from blends.models import (
    NId,
)
from blends.syntax.builders.class_decl import (
    build_class_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    name_n_id = n_attrs["label_field_name"]
    name = graph.nodes[name_n_id].get("label_text", "")
    block_id = n_attrs["label_field_body"]
    return build_class_node(args, name, block_id, None)
