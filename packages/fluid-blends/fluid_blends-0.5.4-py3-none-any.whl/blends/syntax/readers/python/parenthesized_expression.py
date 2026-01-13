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
    childs = adj_ast(args.ast_graph, args.n_id)
    expected_children_for_parenthesized_expression = 3
    c_id = (
        childs[1] if len(childs) == expected_children_for_parenthesized_expression else childs[-2]
    )
    return build_parenthesized_expression_node(args, c_id)
