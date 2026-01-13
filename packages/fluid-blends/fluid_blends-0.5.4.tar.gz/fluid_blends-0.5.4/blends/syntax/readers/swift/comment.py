from blends.models import (
    NId,
)
from blends.syntax.builders.comment import (
    build_comment_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    comment = (
        comment_text
        if (comment_text := args.ast_graph.nodes[args.n_id].get("label_text"))
        else node_to_str(args.ast_graph, args.n_id)
    )

    return build_comment_node(args, comment)
