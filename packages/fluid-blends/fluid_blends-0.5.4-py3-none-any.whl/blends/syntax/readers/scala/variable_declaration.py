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
    var_id = match_ast_d(graph, args.n_id, "val_definition")
    if not var_id:
        var_id = args.n_id

    var_type = None
    if var_type_id := graph.nodes[var_id].get("label_field_type"):
        var_type = graph.nodes[var_type_id].get("label_text")

    var_name_id = graph.nodes[var_id]["label_field_pattern"]
    var_name = node_to_str(graph, var_name_id)

    value_id = graph.nodes[var_id]["label_field_value"]

    return build_variable_declaration_node(args, var_name, var_type, value_id)
