from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
    match_ast_group_d,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    name = "CompanionObject"
    name_id = match_ast_d(graph, args.n_id, "type_identifier")
    if name_id:
        name = node_to_str(graph, name_id)

    block_id = match_ast_d(graph, args.n_id, "class_body")

    modifiers = match_ast_group_d(graph, args.n_id, "modifiers")
    children_nid = {
        "modifiers_id": modifiers,
    }

    return build_method_declaration_node(args, name, block_id, children_nid)
