from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.file import (
    build_file_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    if (body_id := match_ast_d(args.ast_graph, args.n_id, "document")) and (
        block_id := match_ast_d(args.ast_graph, body_id, "block_node")
    ):
        filtered_ids = (
            _id
            for _id in adj_ast(args.ast_graph, block_id)
            if args.ast_graph.nodes[_id]["label_type"] != "---"
        )
        return build_file_node(args, iter(filtered_ids))

    return args.n_id
