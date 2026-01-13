from blends.models import (
    NId,
)
from blends.syntax.builders.symbol_lookup import (
    build_symbol_lookup_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    prefix = node_to_str(args.ast_graph, args.n_id)
    return build_symbol_lookup_node(args, prefix)
