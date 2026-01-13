from blends.models import (
    NId,
)
from blends.syntax.builders.named_argument import (
    build_named_argument_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    field_node = args.ast_graph.nodes[args.n_id]["label_field_name"]
    return build_named_argument_node(args, None, field_node)
