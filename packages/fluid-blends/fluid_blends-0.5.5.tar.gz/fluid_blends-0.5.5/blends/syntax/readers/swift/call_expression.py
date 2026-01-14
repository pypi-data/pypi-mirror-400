from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
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

    arguments_id = match_ast_d(graph, args.n_id, "call_suffix")

    if (
        arguments_id
        and (childs := adj_ast(graph, arguments_id))
        and len(childs) == 1
        and graph.nodes[childs[0]]["label_type"] == "value_arguments"
    ):
        arguments_id = childs[0]

    return build_method_invocation_node(args, expr, expr_id, arguments_id, None)
