from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
    match_ast_d,
)
from blends.syntax.builders.pair import (
    build_pair_node,
)
from blends.syntax.builders.symbol_lookup import (
    build_symbol_lookup_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    name_id = graph.nodes[args.n_id]["label_field_name"]
    type_id = None
    if type_annon_id := graph.nodes[args.n_id].get("label_field_type"):
        type_id = match_ast_d(graph, type_annon_id, "predefined_type")
        if not type_id:
            match_childs = match_ast(graph, type_annon_id, ":")
            type_id = match_childs.get("__0__")

    if type_id:
        return build_pair_node(args, name_id, type_id)
    return build_symbol_lookup_node(args, node_to_str(graph, name_id))
