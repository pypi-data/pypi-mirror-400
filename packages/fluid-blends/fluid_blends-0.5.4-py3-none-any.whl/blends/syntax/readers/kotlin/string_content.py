import re

from blends.models import (
    NId,
)
from blends.syntax.builders.symbol_lookup import build_symbol_lookup_node
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    label_text = args.ast_graph.nodes[args.n_id].get("label_text")
    if not label_text:
        label_text = node_to_str(args.ast_graph, args.n_id)
    symbol = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)", label_text)
    symbol_str = symbol.group(1) if symbol else ""

    return build_symbol_lookup_node(args, symbol_str)
