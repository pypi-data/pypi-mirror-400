from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
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
    arguments_id = args.ast_graph.nodes[args.n_id]["label_field_arguments"]
    expr_id = args.ast_graph.nodes[args.n_id]["label_field_function"]
    expr = node_to_str(args.ast_graph, expr_id)

    if "__0__" not in match_ast(args.ast_graph, arguments_id, "(", ")"):
        arguments_id = None

    return build_method_invocation_node(args, expr, expr_id, arguments_id, None)
