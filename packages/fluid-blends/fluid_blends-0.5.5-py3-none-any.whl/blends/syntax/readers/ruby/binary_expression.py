from blends.models import (
    NId,
)
from blends.syntax.builders.binary_operation import (
    build_binary_operation_node,
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

    operator_str = node_to_str(graph, n_attrs["label_field_operator"])
    left_id = n_attrs["label_field_left"]
    right_id = n_attrs["label_field_right"]

    return build_binary_operation_node(args, operator_str, left_id, right_id)
