from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.return_statement import (
    build_return_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    ignored_labels = {"return", ";"}
    val_id: NId | None = None
    c_ids = [
        _id
        for _id in adj_ast(graph, args.n_id)
        if graph.nodes[_id].get("label_type") not in ignored_labels
    ]
    if c_ids:
        val_id = c_ids[0]

    return build_return_node(args, val_id)
