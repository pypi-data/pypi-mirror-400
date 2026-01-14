from blends.models import (
    NId,
)
from blends.syntax.builders.reserved_word import (
    build_reserved_word_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    val_str = args.ast_graph.nodes[args.n_id].get("label_text") or node_to_str(
        args.ast_graph,
        args.n_id,
    )
    return build_reserved_word_node(args, f"OperatorValue {val_str}")
