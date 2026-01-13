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
    childs = list(adj_ast(graph, args.n_id))
    body_id = match_ast_d(graph, args.n_id, "statements") or childs[-2]

    var_node = graph.nodes[args.n_id]["label_field_item"]

    if it_item := graph.nodes[args.n_id].get("label_field_collection"):
        return build_for_each_statement_node(args, var_node, it_item, body_id)

    return build_for_statement_node(args, var_node, None, None, body_id)
