from blends.models import (
    NId,
)
from blends.syntax.builders.literal import (
    build_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    n_attrs = args.ast_graph.nodes[args.n_id]
    return build_literal_node(args, n_attrs["label_text"], "null")
