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
    _, *c_ids, _ = adj_ast(graph, args.n_id)
    ignored_labels = {
        "\n",
        "\r\n",
    }

    filtered_ids: set[NId] = set()

    for c_id in c_ids:
        label_type = graph.nodes[c_id]["label_type"]
        if label_type == "expression_statement":
            filtered_ids.update(adj_ast(graph, c_id))
        elif label_type in ignored_labels:
            continue
        else:
            filtered_ids.add(c_id)

    return build_execution_block_node(args, iter(filtered_ids))
