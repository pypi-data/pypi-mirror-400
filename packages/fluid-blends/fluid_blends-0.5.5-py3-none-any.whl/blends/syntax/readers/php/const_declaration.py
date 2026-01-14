from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
    match_ast_d,
)
from blends.syntax.builders.variable_declaration import (
    build_variable_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes

    element_id = match_ast_d(graph, args.n_id, "const_element") or args.n_id
    c_ids = match_ast(graph, element_id)

    var_id = c_ids.get("__0__") or ""
    var_name = nodes[var_id].get("label_text") or node_to_str(graph, args.n_id)
    val_id = c_ids.get("__2__")

    return build_variable_declaration_node(args, var_name, None, val_id)
