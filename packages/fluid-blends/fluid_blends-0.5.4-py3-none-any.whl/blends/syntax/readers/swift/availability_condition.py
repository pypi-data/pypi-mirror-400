from blends.models import (
    NId,
)
from blends.syntax.builders.method_invocation import (
    build_method_invocation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import node_to_str


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    expr = node_to_str(graph, args.n_id)

    return build_method_invocation_node(args, expr, None, None, None)
