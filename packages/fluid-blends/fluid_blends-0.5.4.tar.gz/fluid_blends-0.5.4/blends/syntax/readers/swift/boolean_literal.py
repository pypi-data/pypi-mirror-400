from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
)
from blends.syntax.builders.literal import (
    build_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    value = match_ast_d(graph, args.n_id, "true") or ""
    if not value:
        value = match_ast_d(graph, args.n_id, "false") or ""
    value_text = graph.nodes[value]["label_text"]
    return build_literal_node(args, value_text, "bool")
