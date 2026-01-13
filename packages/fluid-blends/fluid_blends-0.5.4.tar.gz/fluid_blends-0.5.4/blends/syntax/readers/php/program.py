from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.file import (
    build_file_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes

    ignored_types = {"php_tag", "empty_statement"}

    c_ids: set[NId] = set()

    for n_id in adj_ast(graph, args.n_id):
        if nodes[n_id].get("label_type") in ignored_types:
            continue

        if (nodes[n_id].get("label_type") == "expression_statement") and (
            c_id := match_ast(graph, n_id).get("__0__")
        ):
            c_ids.add(c_id)
            continue

        c_ids.add(n_id)

    return build_file_node(args, iter(c_ids))
