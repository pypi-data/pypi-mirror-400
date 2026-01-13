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
    n_attrs = args.ast_graph.nodes[args.n_id]
    var_id = n_attrs["label_field_name"]
    val_id = n_attrs["label_field_value"]
    return build_assignment_node(args, var_id, val_id, None)
