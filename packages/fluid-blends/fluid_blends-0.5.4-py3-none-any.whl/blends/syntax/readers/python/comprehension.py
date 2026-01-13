from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.array_node import (
    build_array_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    child_nodes = (
        n_attrs["label_field_body"],
        *match_ast_group_d(graph, args.n_id, "for_in_clause"),
        *match_ast_group_d(graph, args.n_id, "if_clause"),
    )

    return build_array_node(args, child_nodes)
