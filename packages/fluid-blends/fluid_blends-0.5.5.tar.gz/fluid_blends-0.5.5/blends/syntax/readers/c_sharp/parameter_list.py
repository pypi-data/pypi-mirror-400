from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.parameter_list import (
    build_parameter_list_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    labels_to_ignore = {"(", ")", ","}

    c_ids = (
        _id
        for _id in adj_ast(graph, args.n_id)
        if graph.nodes[_id]["label_type"] not in labels_to_ignore
    )

    return build_parameter_list_node(
        args,
        c_ids,
    )
