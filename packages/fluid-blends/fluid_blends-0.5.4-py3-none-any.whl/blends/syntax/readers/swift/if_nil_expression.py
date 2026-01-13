from blends.models import (
    NId,
)
from blends.syntax.builders.if_statement import (
    build_if_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    condition = n_attrs["label_field_value"]
    if_nil = n_attrs.get("label_field_if_nil")
    return build_if_node(args, condition, if_nil, None)
