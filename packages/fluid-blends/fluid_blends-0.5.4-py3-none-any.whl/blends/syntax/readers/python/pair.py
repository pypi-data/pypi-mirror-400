from blends.models import (
    NId,
)
from blends.syntax.builders.pair import (
    build_pair_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    key_id = args.ast_graph.nodes[args.n_id]["label_field_key"]
    value_id = args.ast_graph.nodes[args.n_id]["label_field_value"]
    return build_pair_node(args, key_id, value_id)
