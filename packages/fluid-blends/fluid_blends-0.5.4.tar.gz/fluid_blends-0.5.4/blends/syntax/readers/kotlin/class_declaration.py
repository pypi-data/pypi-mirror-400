from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.class_decl import (
    build_class_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    name = "AnonymousClass"
    name_id = graph.nodes[args.n_id].get("label_field_name") or match_ast_d(
        graph,
        args.n_id,
        "identifier",
    )
    if name_id:
        name = node_to_str(graph, name_id)

    block_id = match_ast_d(graph, args.n_id, "class_body")
    if not block_id:
        block_id = adj_ast(graph, args.n_id)[-1]

    return build_class_node(args, name, block_id, None)
