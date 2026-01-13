from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.if_statement import (
    build_if_node,
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
    conditional_node = None
    invalid_types = {
        "?",
        ":",
    }

    true_block = args.ast_graph.nodes[args.n_id]["label_field_consequence"]
    false_block = args.ast_graph.nodes[args.n_id]["label_field_alternative"]

    reserved_ids = {
        true_block,
        false_block,
    }

    first_child = match_ast(args.ast_graph, args.n_id).get("__0__")
    if (
        first_child
        and args.ast_graph.nodes[first_child]["label_type"] not in invalid_types
        and first_child not in reserved_ids
    ):
        conditional_node = first_child

    if not conditional_node:
        return build_string_literal_node(args, node_to_str(args.ast_graph, args.n_id))

    return build_if_node(args, conditional_node, true_block, false_block)
