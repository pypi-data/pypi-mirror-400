from blends.models import NId
from blends.query import adj_ast, match_ast_group_d
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import SyntaxGraphArgs


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    parameters_list = match_ast_group_d(
        graph,
        args.n_id,
        "lambda_function_type_parameters",
    )

    body_id = None
    for child_id in adj_ast(graph, args.n_id):
        child_attrs = graph.nodes[child_id]
        if child_attrs.get("label_type") in {"statements", "function_body"}:
            body_id = child_id
            break

    children_nid = {
        "parameters_id": parameters_list,
    }
    return build_method_declaration_node(args, None, body_id, children_nid)
