from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.binary_operation import (
    build_binary_operation_node,
)
from blends.syntax.builders.string_literal import (
    build_string_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    operator_id: NId | None = n_attrs.get("label_field_operators") or n_attrs.get(
        "label_field_operator",
    )
    operator = node_to_str(graph, operator_id) if operator_id else ""
    childs = adj_ast(graph, args.n_id)
    if all(
        graph.nodes[_id]["label_type"] == "string"
        for _id in adj_ast(graph, args.n_id)
        if _id != operator_id
    ):
        text = node_to_str(graph, args.n_id)
        return build_string_literal_node(args, text)

    return build_binary_operation_node(args, operator, childs[0], childs[-1])
