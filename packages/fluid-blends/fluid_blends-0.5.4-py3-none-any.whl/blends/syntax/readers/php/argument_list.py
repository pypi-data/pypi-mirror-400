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

    invalid_types = {
        "(",
        ",",
        ")",
    }

    nested_types = {"argument"}

    valid_childs: set[NId] = set()

    for c_id in adj_ast(args.ast_graph, args.n_id):
        if (label_type := graph.nodes[c_id].get("label_type")) in invalid_types:
            continue
        if label_type in nested_types:
            valid_childs.update(adj_ast(graph, c_id))
            continue
        valid_childs.add(c_id)

    return build_argument_list_node(args, iter(valid_childs))
