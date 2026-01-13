from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.file import (
    build_file_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)

    filtered_ids: list[NId] = []
    for _id in c_ids:
        if graph.nodes[_id]["label_type"] == "statement":
            filtered_ids.extend(adj_ast(args.ast_graph, _id))
            continue
        filtered_ids.append(_id)
    return build_file_node(args, iter(filtered_ids))
