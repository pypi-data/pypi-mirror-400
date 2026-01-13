from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.rest_pattern import (
    build_rest_pattern_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    match = match_ast(args.ast_graph, args.n_id, "*", "**")
    identifier_id = match.get("__0__")
    if not identifier_id:
        identifier_id = adj_ast(args.ast_graph, args.n_id)[0]
    return build_rest_pattern_node(args, identifier_id)
