from blends.models import (
    NId,
)
from blends.syntax.builders.literal import (
    build_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    value = node_to_str(args.ast_graph, args.n_id)
    return build_literal_node(args, value, "bool")
