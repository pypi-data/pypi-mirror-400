from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.element_access import (
    build_element_access_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_id = args.n_id

    expr_id = graph.nodes[n_id]["label_field_object"]

    labels_to_ignore = {"[", "]"}
    c_ids = [
        node_id
        for node_id in adj_ast(graph, n_id)
        if graph.nodes[node_id]["label_type"] not in labels_to_ignore and node_id != expr_id
    ]
    arguments_id = c_ids[0] if c_ids else None

    return build_element_access_node(args, expr_id, arguments_id)
