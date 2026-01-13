from blends.models import (
    NId,
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
    text = graph.nodes[args.n_id].get("label_text") or node_to_str(graph, args.n_id)
    return build_string_literal_node(args, text)
