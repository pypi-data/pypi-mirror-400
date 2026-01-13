from blends.models import (
    NId,
)
from blends.query import (
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
    declarator_id = match_ast_d(graph, args.n_id, "var_spec") or match_ast_d(
        graph,
        args.n_id,
        "const_spec",
    )

    if not declarator_id:
        var_name = node_to_str(graph, args.n_id)
        return build_variable_declaration_node(args, var_name, None, None)

    var_id = graph.nodes[declarator_id]["label_field_name"]
    var_name = node_to_str(graph, var_id)
    type_name = None
    if type_id := graph.nodes[declarator_id].get("label_field_type"):
        type_name = node_to_str(graph, type_id)
    value_id = graph.nodes[declarator_id].get("label_field_value")

    return build_variable_declaration_node(args, var_name, type_name, value_id)
