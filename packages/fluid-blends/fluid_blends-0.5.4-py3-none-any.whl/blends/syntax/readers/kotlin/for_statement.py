from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.for_each_statement import (
    build_for_each_statement_node,
)
from blends.syntax.builders.for_statement import (
    build_for_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    class_childs = adj_ast(graph, args.n_id)
    body_id = match_ast_d(graph, args.n_id, "block") or class_childs[0]
    var_node = match_ast_d(graph, args.n_id, "variable_declaration") or class_childs[-1]
    in_node = match_ast_d(graph, args.n_id, "in")

    if graph.nodes[var_node]["label_type"] == "variable_declaration" and (
        s_id := match_ast_d(graph, var_node, "identifier")
    ):
        var_node = s_id

    if in_node:
        iterable_item = class_childs[class_childs.index(in_node) + 1]
        return build_for_each_statement_node(args, var_node, iterable_item, body_id)

    return build_for_statement_node(args, var_node, None, None, body_id)
