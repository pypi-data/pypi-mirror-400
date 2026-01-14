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
    types = {
        "array_type",
        "channel_type",
        "function_type",
        "generic_type",
        "interface_type",
        "map_type",
        "pointer_type",
        "qualified_type",
        "slice_type",
        "struct_type",
        "type_identifier",
    }
    var_name = None
    var_type = None

    if spec_id := match_ast_d(graph, args.n_id, "type_spec"):
        id_name = graph.nodes[spec_id]["label_field_name"]
        var_name = node_to_str(graph, id_name)
        for t_id in adj_ast(graph, spec_id):
            if graph.nodes[t_id]["label_type"] in types:
                var_type = node_to_str(graph, t_id)

    if not var_name:
        var_name = node_to_str(graph, args.n_id)

    return build_variable_declaration_node(args, var_name, var_type, None)
