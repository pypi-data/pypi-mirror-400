from blends.models import (
    NId,
)
from blends.query import (
    get_node_by_path,
    match_ast_d,
    match_ast_group_d,
)
from blends.syntax.builders.class_decl import (
    build_class_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    class_node = args.ast_graph.nodes[args.n_id]
    declaration_n_id = match_ast_d(args.ast_graph, args.n_id, "identifier") or ""
    declaration_node = args.ast_graph.nodes[declaration_n_id]
    declaration_line = declaration_node["label_l"]
    args.ast_graph.nodes[args.n_id]["label_l"] = declaration_line
    name_id = class_node["label_field_name"]
    block_id = class_node["label_field_body"]
    name = node_to_str(args.ast_graph, name_id)
    attrl_ids = match_ast_group_d(args.ast_graph, args.n_id, "attribute_list")
    inherited_id = get_node_by_path(args.ast_graph, args.n_id, "base_list", "identifier")
    inherited_class = node_to_str(args.ast_graph, inherited_id) if inherited_id else None

    return build_class_node(args, name, block_id, attrl_ids, inherited_class)
