from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.return_statement import (
    build_return_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    childs = match_ast(graph, args.n_id, "return")
    expected_children_for_return_with_value = 2
    if len(childs) == expected_children_for_return_with_value and (stmt_id := childs["__0__"]):
        if (
            graph.nodes[stmt_id]["label_type"] == "expression_list"
            and (expr_childs := adj_ast(graph, stmt_id))
            and len(expr_childs) == 1
        ):
            return build_return_node(args, expr_childs[0])

        return build_return_node(args, stmt_id)

    return build_return_node(args, None)
