from blends.models import (
    NId,
)
from blends.syntax.builders.unary_expression import (
    build_unary_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    value_id = n_attrs["label_field_operand"]
    operand = node_to_str(graph, n_attrs["label_field_type"])

    return build_unary_expression_node(args, operand, value_id)
