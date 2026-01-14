from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.expression_statement import (
    build_expression_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs_id = adj_ast(args.ast_graph, args.n_id)
    ignore_types = {"[", "]", ":"}

    valid_childs = [
        child
        for child in childs_id
        if args.ast_graph.nodes[child]["label_type"] not in ignore_types
    ]

    return build_expression_statement_node(args, iter(valid_childs))
