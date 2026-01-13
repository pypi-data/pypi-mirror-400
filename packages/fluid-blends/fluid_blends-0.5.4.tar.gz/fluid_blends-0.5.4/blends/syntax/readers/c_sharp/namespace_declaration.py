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
    namespace = args.ast_graph.nodes[args.n_id]
    block_id = namespace["label_field_body"]
    name = node_to_str(args.ast_graph, namespace["label_field_name"])
    return build_namespace_node(args, name, block_id)
