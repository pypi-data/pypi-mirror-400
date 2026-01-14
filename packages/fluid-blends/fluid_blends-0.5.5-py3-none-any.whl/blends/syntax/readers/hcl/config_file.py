from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.file import (
    build_file_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    body_id = match_ast_d(args.ast_graph, args.n_id, "body")
    c_ids = adj_ast(args.ast_graph, body_id) if body_id else adj_ast(args.ast_graph, args.n_id)
    return build_file_node(args, iter(c_ids))
