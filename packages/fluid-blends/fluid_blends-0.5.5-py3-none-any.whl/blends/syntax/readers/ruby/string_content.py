from blends.models import (
    NId,
)
from blends.query import match_ast_d, match_ast_group_d, pred_ast
from blends.syntax.builders.string_literal import build_string_literal_node
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import node_to_str


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    text = node_to_str(graph, args.n_id)
    parent = pred_ast(graph, args.n_id)[0]
    c_ids = []
    if graph.nodes[parent]["label_type"] == "subshell" and (
        interpolation := match_ast_d(graph, parent, "interpolation")
    ):
        identifiers = match_ast_group_d(graph, interpolation, "identifier")
        element_refs = match_ast_group_d(graph, interpolation, "element_reference")
        c_ids = identifiers + element_refs
    return build_string_literal_node(args, text, iter(c_ids) if c_ids else None)
