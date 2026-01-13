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

    c_ids = match_ast(graph, args.n_id, "new", "arguments")
    name = ""
    initializer_id = c_ids.get("__0__")
    if initializer_id:
        name = node_to_str(graph, initializer_id)

        if graph.nodes[initializer_id]["label_type"] in {"name", "qualified_name"}:
            initializer_id = None

    arguments_id = c_ids.get("arguments")

    return build_object_creation_node(args, name, arguments_id, initializer_id)
