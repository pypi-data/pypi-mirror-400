from blends.models import (
    NId,
)
from blends.syntax.builders.namespace import (
    build_namespace_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    if label_n_id := graph.nodes[args.n_id].get("label_field_name"):
        name = node_to_str(graph, label_n_id).replace("\\", "/")
    else:
        name = "anonymous_namespace"

    block_id = graph.nodes[args.n_id].get("label_field_body")

    return build_namespace_node(args, name, block_id)
