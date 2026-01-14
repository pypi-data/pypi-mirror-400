from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
    match_ast_group_d,
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
    decl_id = match_ast_d(graph, args.n_id, "variable_declaration")
    if not decl_id:
        decl_id = adj_ast(graph, args.n_id)[0]

    var_type_id = graph.nodes[decl_id]["label_field_type"]
    var_type = node_to_str(graph, var_type_id)
    value_id = None

    var_decl_id = match_ast_d(graph, decl_id, "variable_declarator")
    if not var_decl_id:
        var_decl_id = adj_ast(graph, decl_id)[-1]

    if identifier_ids := match_ast_group_d(graph, var_decl_id, "identifier"):
        var_name = node_to_str(graph, identifier_ids[0])
    else:
        var_name = node_to_str(graph, adj_ast(graph, var_decl_id)[0])

    value_id = None
    if len(identifier_ids) > 1:
        value_id = identifier_ids[-1]
    elif (declarator_id := match_ast_d(graph, decl_id, "variable_declarator")) and (
        declarator_childs := list(
            filter(
                lambda child: graph.nodes[child]["label_type"] not in ("identifier", "="),
                list(adj_ast(graph, declarator_id)),
            ),
        )
    ):
        value_id = declarator_childs[0]

    return build_variable_declaration_node(args, var_name, var_type, value_id)
