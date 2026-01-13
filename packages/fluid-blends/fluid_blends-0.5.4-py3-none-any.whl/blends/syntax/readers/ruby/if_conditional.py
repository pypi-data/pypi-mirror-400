from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
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

    condition_id = n_attrs.get("label_field_condition") or adj_ast(graph, args.n_id)[0]
    true_id = n_attrs.get("label_field_consequence")
    false_id = n_attrs.get("label_field_alternative")

    return build_if_node(args, condition_id, true_id, false_id)
