from blends.models import (
    NId,
)
from blends.syntax.builders.assignment import (
    build_assignment_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    as_attrs = args.ast_graph.nodes[args.n_id]
    var_id = as_attrs["label_field_left"]
    val_id = as_attrs["label_field_right"]
    op_id = as_attrs["label_field_operator"]
    operation = args.ast_graph.nodes[op_id]["label_text"]
    return build_assignment_node(args, var_id, val_id, operation)
