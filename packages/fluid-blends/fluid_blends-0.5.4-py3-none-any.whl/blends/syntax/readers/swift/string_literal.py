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
    n_attrs = args.ast_graph.nodes[args.n_id]
    label_text = node_to_str(graph, args.n_id)
    if text_nid := n_attrs.get("label_field_text"):
        label_text = args.ast_graph.nodes[text_nid].get("label_text", "")

    ints = match_ast_group_d(graph, args.n_id, "interpolated_expression")
    int_subs = [adj_ast(graph, _id)[0] for _id in ints]

    if len(int_subs) > 0:
        return build_string_literal_node(args, label_text, iter(int_subs))

    return build_string_literal_node(args, label_text)
