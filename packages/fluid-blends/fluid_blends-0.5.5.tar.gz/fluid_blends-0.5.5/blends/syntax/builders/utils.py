from blends.models import (
    NId,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def bound_identifier_symbol(args: SyntaxGraphArgs, *, var_id: NId) -> str | None:
    var_node = args.ast_graph.nodes.get(var_id, {})
    if var_node.get("label_type") != "identifier":
        return None
    symbol = node_to_str(args.ast_graph, var_id)
    return symbol if symbol else None
