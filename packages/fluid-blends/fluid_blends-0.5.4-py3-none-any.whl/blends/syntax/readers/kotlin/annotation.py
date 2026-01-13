from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.annotation import (
    build_annotation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    args_id = None
    annotation_name = "@"

    constructor_id = match_ast_d(args.ast_graph, args.n_id, "constructor_invocation")
    if (
        constructor_id
        and (children := adj_ast(args.ast_graph, constructor_id))
        and len(children) > 0
    ):
        annotation_name += node_to_str(args.ast_graph, children[0])
        args_id = children[1]

    return build_annotation_node(args, annotation_name, args_id)
