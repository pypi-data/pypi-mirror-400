from blends.models import (
    NId,
)
from blends.query import (
    get_nodes_by_path,
    match_ast_d,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    body_id = match_ast_d(args.ast_graph, args.n_id, "infix_expression") or match_ast_d(
        args.ast_graph, args.n_id, "indented_block"
    )
    children = {}
    if param_id := graph.nodes[args.n_id].get("label_field_parameters"):
        children["parameters_id"] = [param_id]
    elif condition_nodes := get_nodes_by_path(graph, args.n_id, set(), "bindings", "binding"):
        children["parameters_id"] = list(condition_nodes)

    return build_method_declaration_node(args, "LambdaExpression", body_id, children)
