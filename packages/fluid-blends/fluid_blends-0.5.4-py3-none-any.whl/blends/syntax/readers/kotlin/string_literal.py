import re

from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_group_d,
)
from blends.syntax.builders.string_literal import (
    build_string_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    literal_text = n_attrs.get("label_text") or node_to_str(graph, args.n_id)

    ints = match_ast_group_d(graph, args.n_id, "interpolation")
    int_subs = [adj_ast(graph, _id)[1] for _id in ints]

    vars_content = list(adj_ast(graph, args.n_id))
    for index, node_id in enumerate(vars_content):
        if (
            (graph.nodes[node_id].get("label_type") == "string_content")
            and (graph.nodes[node_id].get("label_text") == "$")
            and ((index + 1) < len(vars_content))
            and (next_node := vars_content[index + 1])
            and (label_text := graph.nodes[next_node].get("label_text"))
            and (re.match(r"^[a-zA-Z_]", label_text))
        ):
            int_subs.append(next_node)

    if len(int_subs) > 0:
        return build_string_literal_node(args, literal_text, iter(int_subs))

    return build_string_literal_node(args, literal_text)
