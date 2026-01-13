from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.execution_block import (
    build_execution_block_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    labels_to_ignore = {"else", "do", "end", ";", "{", "}"}
    c_ids = (
        node_id
        for node_id in adj_ast(graph, args.n_id)
        if graph.nodes[node_id]["label_type"] not in labels_to_ignore
    )

    return build_execution_block_node(args, c_ids)
