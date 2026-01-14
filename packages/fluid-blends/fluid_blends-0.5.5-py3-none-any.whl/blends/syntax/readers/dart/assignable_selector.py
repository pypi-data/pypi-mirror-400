from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.selector import (
    build_selector_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    c_ids = [
        child
        for child in adj_ast(graph, args.n_id)
        if args.ast_graph.nodes[child]["label_type"] in {"identifier", "index_selector"}
    ]

    return build_selector_node(args, None, iter(c_ids))
