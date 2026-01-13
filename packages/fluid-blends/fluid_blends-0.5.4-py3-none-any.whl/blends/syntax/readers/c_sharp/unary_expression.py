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
    operator_id = graph.nodes[args.n_id]["label_field_operator"]
    operator = graph.nodes[operator_id]["label_text"]
    operand_id = graph.nodes[args.n_id]["label_field_argument"]
    return build_unary_expression_node(args, operator, operand_id)
