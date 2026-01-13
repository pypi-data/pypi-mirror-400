from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.file import (
    build_file_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    c_ids = (
        n_id
        for n_id in adj_ast(args.ast_graph, args.n_id)
        if args.ast_graph.nodes[n_id].get("label_type") != "empty_statement"
    )
    return build_file_node(args, c_ids)
