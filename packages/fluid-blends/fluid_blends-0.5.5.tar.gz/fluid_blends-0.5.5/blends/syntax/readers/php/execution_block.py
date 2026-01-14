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

    ignored_types = {"{", "}", "global_declaration"}
    c_ids = (
        _id
        for _id in adj_ast(graph, args.n_id)
        if graph.nodes[_id].get("label_type") not in ignored_types
    )

    return build_execution_block_node(args, c_ids)
