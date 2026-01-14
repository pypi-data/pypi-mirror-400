from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_group_d,
)
from blends.syntax.builders.array_node import (
    build_array_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes

    c_ids: set[NId] = set()

    for _id in match_ast_group_d(graph, args.n_id, "array_element_initializer"):
        element_c_ids = adj_ast(graph, _id)

        for c_id in element_c_ids:
            if nodes[c_id].get("label_type") == "=>":
                c_ids.add(c_id)
                break
        else:
            c_ids.update(element_c_ids)

    return build_array_node(args, iter(c_ids))
