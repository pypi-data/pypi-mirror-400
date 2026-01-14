from blends.models import (
    NId,
)
from blends.syntax.builders.for_statement import (
    build_for_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    body_id = n_attrs["label_field_body"]
    var_node = n_attrs["label_field_pattern"]
    condition_node = n_attrs["label_field_value"]

    return build_for_statement_node(args, var_node, condition_node, None, body_id)
