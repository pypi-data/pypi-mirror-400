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
    index_id = n_attrs["label_field_index"]
    expr_id = n_attrs["label_field_object"]
    return build_element_access_node(args, expr_id, index_id)
