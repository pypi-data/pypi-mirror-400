from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.import_global import (
    build_import_global_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    name: str = ""
    node_ids: set[NId] = set[NId]()

    for idx, node_id in match_ast(graph, args.n_id).items():
        if not node_id:
            continue

        if idx == "__0__":
            name = node_to_str(graph, node_id)
            continue

        if graph.nodes[node_id]["label_type"] == "parenthesized_expression":
            node_ids.add(adj_ast(graph, node_id)[1])
        else:
            node_ids.add(node_id)

    return build_import_global_node(args, name, node_ids, None)
