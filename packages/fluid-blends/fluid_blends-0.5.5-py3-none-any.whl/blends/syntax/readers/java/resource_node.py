from blends.models import (
    NId,
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
    n_attrs = graph.nodes[args.n_id]
    value_id = n_attrs.get("label_field_value")
    name_id = n_attrs.get("label_field_name")
    var_name = node_to_str(graph, name_id) if name_id else node_to_str(graph, args.n_id)
    type_id = n_attrs.get("label_field_type")
    var_type = node_to_str(graph, type_id) if type_id else None

    return build_variable_declaration_node(args, var_name, var_type, value_id)
