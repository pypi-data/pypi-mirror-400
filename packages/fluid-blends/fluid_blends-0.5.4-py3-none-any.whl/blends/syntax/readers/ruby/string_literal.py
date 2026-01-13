from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_group_d,
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
    graph, n_id = args.ast_graph, args.n_id
    text = node_to_str(graph, n_id)

    interpolations = match_ast_group_d(graph, n_id, "interpolation")
    valid_nodes = [
        child_id
        for interp in interpolations
        for child_id in adj_ast(graph, interp)
        if graph.nodes[child_id]["label_type"] in {"identifier", "element_reference"}
    ]

    return (
        build_string_literal_node(args, text, iter(valid_nodes))
        if valid_nodes
        else build_string_literal_node(args, text)
    )
