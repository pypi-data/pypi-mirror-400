from blends.models import (
    NId,
)
from blends.syntax.builders.symbol_lookup import (
    build_symbol_lookup_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    symbol = args.ast_graph.nodes[args.n_id]["label_text"]
    return build_symbol_lookup_node(args, symbol)
