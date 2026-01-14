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
    graph = args.ast_graph
    node_attr = graph.nodes[args.n_id]
    type_id = node_attr["label_field_type"]
    name = node_to_str(graph, type_id)

    if arguments_id := node_attr.get("label_field_arguments"):
        if "__0__" not in match_ast(graph, arguments_id, "(", ")"):
            arguments_id = None
        return build_object_creation_node(args, name, arguments_id, None)

    init_id = node_attr.get("label_field_initializer")
    if (
        init_id
        and (childs := match_ast(graph, init_id, "assignment_expression"))
        and not childs.get("__0__")
    ):
        init_id = None

    return build_object_creation_node(args, name, None, init_id)
