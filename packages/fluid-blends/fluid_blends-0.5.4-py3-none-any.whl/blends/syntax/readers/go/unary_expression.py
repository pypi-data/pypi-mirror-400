from blends.models import NId
from blends.syntax.builders.unary_expression import build_unary_expression_node
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    operator = (
        graph.nodes[operator_id]["label_text"]
        if (operator_id := n_attrs.get("label_field_operator"))
        else ""
    )
    return build_unary_expression_node(args, operator, NId(n_attrs["label_field_operand"]))
