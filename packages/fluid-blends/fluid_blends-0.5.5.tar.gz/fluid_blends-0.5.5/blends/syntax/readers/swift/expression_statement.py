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
    expr_ids = [
        _id
        for _id in adj_ast(args.ast_graph, args.n_id)
        if args.ast_graph.nodes[_id]["label_type"] not in {"(", ")", ","}
    ]
    return build_expression_statement_node(args, iter(expr_ids))
