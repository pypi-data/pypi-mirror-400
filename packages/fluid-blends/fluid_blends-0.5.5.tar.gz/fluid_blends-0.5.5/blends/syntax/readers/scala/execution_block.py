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
    all_ids = adj_ast(graph, args.n_id)
    delimiter_types = {"{", "}", ":", "(", ")", ","}
    c_ids = [n_id for n_id in all_ids if graph.nodes[n_id].get("label_type") not in delimiter_types]

    return build_execution_block_node(
        args,
        c_ids=(_id for _id in c_ids),
    )
