from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.if_statement import (
    build_if_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs = match_ast(args.ast_graph, args.n_id, "if", "else")
    expected_match_count_for_conditional_with_else = 5
    if (
        childs["if"]
        and childs["else"]
        and len(childs) == expected_match_count_for_conditional_with_else
    ):
        return build_if_node(args, str(childs["__1__"]), childs["__0__"], childs["__2__"])
    return build_if_node(args, str(childs["__0__"]))
