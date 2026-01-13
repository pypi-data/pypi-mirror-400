from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
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
    var_id = match_ast_d(graph, args.n_id, "variable_declaration")
    mod_n = match_ast_d(graph, args.n_id, "modifier")
    c_mod_n = None
    if (mod_n := match_ast_d(graph, args.n_id, "modifier")) and (adj := adj_ast(graph, mod_n)):
        c_mod_n = node_to_str(graph, adj[0])

    if not var_id:
        var_id = args.n_id

    var_type_id = graph.nodes[var_id]["label_field_type"]
    var_type = node_to_str(graph, var_type_id)

    var_decl_id = match_ast_d(graph, var_id, "variable_declarator")
    if not var_decl_id:
        var_decl_id = adj_ast(graph, var_id)[0]

    childs = match_ast(graph, var_decl_id, "identifier")
    if identifier_id := childs.get("identifier"):
        var_name = node_to_str(graph, identifier_id)
    else:
        var_name = node_to_str(graph, var_decl_id)

    value_id = None
    if (declarator_id := match_ast_d(graph, var_id, "variable_declarator")) and (
        declarator_childs := list(
            filter(
                lambda child: graph.nodes[child]["label_type"] not in ("identifier", "="),
                list(adj_ast(graph, declarator_id)),
            ),
        )
    ):
        value_id = declarator_childs[0]

    return build_variable_declaration_node(args, var_name, var_type, value_id, None, c_mod_n)
