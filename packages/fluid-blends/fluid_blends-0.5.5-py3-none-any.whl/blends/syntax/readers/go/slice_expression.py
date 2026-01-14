from blends.models import (
    NId,
)
from blends.syntax.builders.element_access import (
    build_element_access_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    n_attrs = args.ast_graph.nodes[args.n_id]
    operand_id = n_attrs["label_field_operand"]
    start_id = n_attrs.get("label_field_start")

    return build_element_access_node(args, operand_id, start_id)
