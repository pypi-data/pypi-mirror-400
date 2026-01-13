from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
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
    node_attr = args.ast_graph.nodes[args.n_id]
    type_id = node_attr["label_field_type"]
    name = node_to_str(args.ast_graph, type_id)

    arguments_id = node_attr["label_field_arguments"]
    if "__0__" not in match_ast(args.ast_graph, arguments_id, "(", ")"):
        arguments_id = None
    init_node: str | None = match_ast(args.ast_graph, args.n_id, "class_body").get("class_body")

    return build_object_creation_node(args, name, arguments_id, init_node)
