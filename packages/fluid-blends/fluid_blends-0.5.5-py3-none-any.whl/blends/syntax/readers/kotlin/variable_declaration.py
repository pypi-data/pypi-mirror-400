from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
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
    var_name = "Unnamed"
    var_type = None

    var_dec = match_ast_d(graph, args.n_id, "variable_declaration")
    if var_dec:
        name = match_ast_d(graph, var_dec, "identifier")
        if name:
            var_name = node_to_str(graph, name)

        var_type_id = match_ast_d(graph, var_dec, "user_type")
        if var_type_id:
            var_type = node_to_str(graph, var_type_id)

    value_id = adj_ast(graph, args.n_id)[-1]
    if graph.nodes[value_id]["label_type"] in {
        "property_delegate",
        "variable_declaration",
    }:
        val_id = match_ast_d(graph, value_id, "call_expression")
        return build_variable_declaration_node(args, var_name, var_type, val_id)

    return build_variable_declaration_node(args, var_name, var_type, value_id)
