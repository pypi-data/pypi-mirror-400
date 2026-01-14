from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.new_expression import (
    build_new_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs = adj_ast(args.ast_graph, args.n_id)
    args_id = match_ast_d(args.ast_graph, args.n_id, "arguments")
    const_id = childs[1]
    return build_new_expression_node(args, const_id, args_id)
