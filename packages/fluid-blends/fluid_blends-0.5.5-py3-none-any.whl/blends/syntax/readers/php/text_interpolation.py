from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
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
    value = ""
    text_id = match_ast_d(graph, args.n_id, "text")
    if text_id:
        value = node_to_str(graph, text_id)

    return build_string_literal_node(args, value)
