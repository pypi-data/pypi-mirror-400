from blends.models import (
    NId,
)
from blends.syntax.builders.assignment import (
    build_assignment_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    n_attrs = args.ast_graph.nodes[args.n_id]
    var_id = n_attrs["label_field_left"]
    val_id = n_attrs["label_field_right"]
    if op_id := n_attrs.get("label_field_operator"):
        operator = node_to_str(args.ast_graph, op_id)
    else:
        operator = None

    return build_assignment_node(args, var_id, val_id, operator)
