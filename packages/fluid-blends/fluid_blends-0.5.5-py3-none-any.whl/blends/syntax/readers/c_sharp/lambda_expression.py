from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
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
    n_attrs = graph.nodes[args.n_id]
    body_id = n_attrs["label_field_body"]
    param_id = (
        match_ast_d(graph, args.n_id, "identifier")
        or match_ast_d(graph, args.n_id, "parameter_list")
        or adj_ast(graph, args.n_id)[0]
    )

    children = {"parameters_id": [param_id]}

    return build_method_declaration_node(args, "LambdaExpression", body_id, children)
