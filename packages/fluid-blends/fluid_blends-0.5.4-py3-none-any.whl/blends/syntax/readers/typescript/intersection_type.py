from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.new_expression import (
    build_new_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs = match_ast(args.ast_graph, args.n_id, "&")
    const_id = childs.get("__0__")
    if not const_id:
        const_id = adj_ast(args.ast_graph, args.n_id)[0]

    args_id = childs.get("__1__")
    return build_new_expression_node(args, const_id, args_id)
