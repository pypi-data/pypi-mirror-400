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
    text = graph.nodes[args.n_id].get("label_text") or node_to_str(graph, args.n_id)
    ints = match_ast_group_d(graph, args.n_id, "template_substitution")
    int_subs = [adj_ast(graph, _id)[1] for _id in ints]
    if len(int_subs) > 0:
        return build_string_literal_node(args, text, iter(int_subs))

    return build_string_literal_node(args, text)
