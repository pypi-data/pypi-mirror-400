from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.for_each_statement import (
    build_for_each_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    node = graph.nodes[args.n_id]
    childs = adj_ast(graph, args.n_id)
    var_node = node.get("label_field_left") or childs[0]
    iterable_item = node.get("label_field_right") or childs[-1]
    block_id = node.get("label_field_body")

    if block_id and graph.nodes[block_id]["label_type"] == "expression_statement":
        block_id = match_ast(graph, block_id)["__0__"]

    return build_for_each_statement_node(args, var_node, iterable_item, block_id)
