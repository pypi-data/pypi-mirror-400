from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.unary_expression import (
    build_unary_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    match = match_ast(graph, args.n_id, ":")
    type_id = match.get("__0__") or adj_ast(graph, args.n_id)[-1]
    return build_unary_expression_node(args, "Typeof", type_id)
