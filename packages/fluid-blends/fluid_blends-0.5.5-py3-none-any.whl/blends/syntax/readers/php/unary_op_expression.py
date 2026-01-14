from blends.models import (
    NId,
)
from blends.query import (
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
    c_ids = match_ast(graph, args.n_id)
    operator_n_id = c_ids.get("__0__") or ""
    operator = graph.nodes[operator_n_id].get("label_text", "")
    operand = c_ids.get("__1__") or args.n_id

    return build_unary_expression_node(args, operator, operand)
