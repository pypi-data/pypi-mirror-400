from blends.models import (
    NId,
)
from blends.syntax.builders.ternary_operation import (
    build_ternary_operation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    n_attrs = args.ast_graph.nodes[args.n_id]
    cond_id = n_attrs["label_field_condition"]
    alt_id = n_attrs["label_field_alternative"]
    cons_id = n_attrs["label_field_consequence"]
    return build_ternary_operation_node(args, cond_id, alt_id, cons_id)
