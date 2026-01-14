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
    c_ids = adj_ast(graph, args.n_id)
    invalid_childs = {"=>", ";", "async"}

    return build_execution_block_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"] not in invalid_childs),
    )
