from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_group,
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
    expr_id = adj_ast(graph, args.n_id)[0]
    expr = node_to_str(graph, expr_id)

    matches = match_ast_group(graph, args.n_id, "value_arguments", "annotated_lambda")

    args_id = None
    if value_arguments := matches.get("value_arguments"):
        args_id = value_arguments[0]

    extra_fields = {}
    if (annotated_lambda := matches.get("annotated_lambda")) and (
        lambda_children := adj_ast(graph, annotated_lambda[0], label_type="lambda_literal")
    ):
        extra_fields["object_id"] = lambda_children[0]

    return build_method_invocation_node(args, expr, expr_id, args_id, extra_fields)
