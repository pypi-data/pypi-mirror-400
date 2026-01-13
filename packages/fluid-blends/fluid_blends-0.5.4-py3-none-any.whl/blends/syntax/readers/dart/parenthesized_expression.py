from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.parenthesized_expression import (
    build_parenthesized_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    expr_id = adj_ast(args.ast_graph, args.n_id)[1]
    return build_parenthesized_expression_node(args, expr_id)
