from blends.models import (
    NId,
)
from blends.syntax.builders.method_invocation import (
    build_method_invocation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    expr_id = graph.nodes[args.n_id]["label_field_function"]
    expr = node_to_str(graph, expr_id)

    arguments_id = graph.nodes[args.n_id]["label_field_arguments"]

    return build_method_invocation_node(args, expr, expr_id, arguments_id, None)
