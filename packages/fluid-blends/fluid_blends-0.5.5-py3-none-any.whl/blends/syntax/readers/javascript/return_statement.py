from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.return_statement import (
    build_return_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    match = match_ast(args.ast_graph, args.n_id, "return", ";")
    expected_match_count_for_return_with_value = 3
    if len(match) == expected_match_count_for_return_with_value:
        return build_return_node(args, value_id=str(match["__0__"]))
    return build_return_node(args, None)
