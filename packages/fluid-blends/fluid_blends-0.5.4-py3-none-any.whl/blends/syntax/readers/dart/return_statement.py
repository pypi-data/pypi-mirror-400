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
    match = match_ast(args.ast_graph, args.n_id, "return", "yield", ";")
    min_match_count_for_selector_return = 5
    min_match_count_for_value_return = 3
    if (
        len(match) > min_match_count_for_selector_return
        and (n_id := match.get("__1__"))
        and args.ast_graph.nodes[n_id]["label_type"] == "selector"
    ):
        return build_return_node(args, value_id=str(match["__1__"]))
    if len(match) > min_match_count_for_value_return:
        return build_return_node(args, value_id=str(match["__0__"]))
    return build_return_node(args, None)
