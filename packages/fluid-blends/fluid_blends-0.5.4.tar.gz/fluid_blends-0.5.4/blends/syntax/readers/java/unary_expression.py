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
    node_id = args.ast_graph.nodes[args.n_id]
    operator = args.ast_graph.nodes[node_id["label_field_operator"]]["label_text"]
    operand = node_id["label_field_operand"]
    return build_unary_expression_node(args, operator, operand)
