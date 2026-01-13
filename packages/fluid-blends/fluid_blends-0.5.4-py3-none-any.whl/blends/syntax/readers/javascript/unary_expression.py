from blends.models import (
    NId,
)
from blends.syntax.builders.unary_expression import (
    build_unary_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    operator = graph.nodes[n_attrs["label_field_operator"]]["label_text"]
    operand = n_attrs["label_field_argument"]
    return build_unary_expression_node(args, operator, operand)
