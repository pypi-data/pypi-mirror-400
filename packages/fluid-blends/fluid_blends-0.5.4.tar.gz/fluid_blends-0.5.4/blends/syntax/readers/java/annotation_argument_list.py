from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.argument_list import (
    build_argument_list_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    _, *c_ids, _ = adj_ast(graph, args.n_id)  # do not consider ( )

    return build_argument_list_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"] != ","),
    )
