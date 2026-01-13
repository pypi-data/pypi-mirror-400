from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
    match_ast_d,
)
from blends.syntax.builders.method_invocation import (
    build_method_invocation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes

    if nodes[args.n_id]["label_type"] == "print_intrinsic":
        childs = adj_ast(graph, args.n_id)
        if (
            len(childs) > 1
            and (child_id := childs[1])
            and nodes[child_id]["label_type"] == "parenthesized_expression"
            and (c_ids := match_ast(graph, child_id))
        ):
            expr_id = c_ids["__1__"]
        else:
            expr_id = None
        return build_method_invocation_node(args, "print", expr_id, None, None)

    if nodes[args.n_id]["label_type"] == "exit_statement":
        args_id = match_ast(graph, args.n_id).get("__2__", None)
        return build_method_invocation_node(args, "exit", None, args_id, None)

    args_id = match_ast_d(args.ast_graph, args.n_id, "echo")
    return build_method_invocation_node(args, "echo", None, args_id, None)
