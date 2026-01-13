from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.execution_block import (
    build_execution_block_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    if expr := match_ast_d(graph, args.n_id, "expression") or (
        expr := match_ast_d(graph, args.n_id, "comparison_expression")
    ):
        c_ids = [expr]
    else:
        c_ids = [
            n_id
            for n_id in adj_ast(graph, args.n_id)
            if graph.nodes[n_id]["label_type"] not in {"{", "}"}
        ]
    return build_execution_block_node(args, iter(c_ids))
