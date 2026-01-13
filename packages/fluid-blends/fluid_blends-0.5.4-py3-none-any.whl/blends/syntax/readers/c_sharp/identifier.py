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
    symbol = args.ast_graph.nodes[args.n_id].get("label_text")
    if not symbol:
        symbol = node_to_str(args.ast_graph, args.n_id)
    return build_symbol_lookup_node(args, symbol)
