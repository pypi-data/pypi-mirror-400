from collections.abc import (
    Iterator,
)

from blends.models import (
    Graph,
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_group_d,
)
from blends.syntax.builders.argument_list import (
    build_argument_list_node,
)
from blends.syntax.builders.string_literal import (
    build_string_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def get_filtered_childs_text(graph: Graph, n_id: str) -> Iterator[str]:
    for c_id in adj_ast(graph, n_id):
        yield from get_filtered_childs_text(graph, c_id)
    if "label_text" in graph.nodes[n_id] and graph.nodes[n_id].get("label_type") not in [
        "interpreted_string_literal",
        "raw_string_literal",
    ]:
        yield graph.nodes[n_id]["label_text"]


def reader(args: SyntaxGraphArgs) -> NId:
    childs = match_ast_group_d(args.ast_graph, args.n_id, "keyed_element")
    if len(childs) > 0:
        return build_argument_list_node(args, iter(childs))
    literal_args = []
    if literals := match_ast_group_d(args.ast_graph, args.n_id, "literal_element"):
        for literal in literals:
            if call_expression := match_ast_group_d(args.ast_graph, literal, "call_expression"):
                literal_args.extend(call_expression)
            else:
                literal_args.extend(adj_ast(args.ast_graph, literal))
        return build_argument_list_node(args, iter(literal_args))

    value = "".join(get_filtered_childs_text(args.ast_graph, args.n_id))
    return build_string_literal_node(args, value)
