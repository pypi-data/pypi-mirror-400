from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_group_d,
)
from blends.syntax.builders.file import (
    build_file_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    ignored_labels = {
        "\n",
        "\r\n",
    }
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)

    filtered_ids = []
    for _id in c_ids:
        if (label_type := graph.nodes[_id]["label_type"]) in ignored_labels:
            continue
        if label_type == "import_declaration":
            filtered_ids.extend(match_ast_group_d(args.ast_graph, _id, "import_spec", depth=2))
            continue
        filtered_ids.append(_id)

    return build_file_node(args, filtered_ids)
