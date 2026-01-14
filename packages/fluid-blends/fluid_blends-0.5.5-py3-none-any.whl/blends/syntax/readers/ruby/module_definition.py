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
    n_attrs = graph.nodes[args.n_id]

    name_id = n_attrs["label_field_name"]
    name_str = node_to_str(graph, name_id)
    block_id = n_attrs.get("label_field_body")

    return build_namespace_node(args, name_str, block_id)
