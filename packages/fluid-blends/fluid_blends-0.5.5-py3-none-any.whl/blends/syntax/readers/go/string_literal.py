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
    n_attrs = args.ast_graph.nodes[args.n_id]
    text = n_attrs.get("label_text") or node_to_str(args.ast_graph, args.n_id)
    return build_string_literal_node(args, text)
