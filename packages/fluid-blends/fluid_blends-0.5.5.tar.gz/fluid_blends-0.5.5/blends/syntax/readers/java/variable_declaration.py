from blends.models import (
    NId,
)
from blends.syntax.builders.variable_declaration import (
    build_variable_declaration_node,
)
from blends.syntax.metadata.java import (
    add_instance_to_metadata,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    var_type_id = args.ast_graph.nodes[args.n_id]["label_field_type"]
    var_type = node_to_str(args.ast_graph, var_type_id)

    declarator_id = args.ast_graph.nodes[args.n_id]["label_field_declarator"]

    var_id = args.ast_graph.nodes[declarator_id]["label_field_name"]
    var_name = node_to_str(args.ast_graph, var_id)

    value_id = args.ast_graph.nodes[declarator_id].get("label_field_value")

    if args.syntax_graph.nodes.get("0"):
        add_instance_to_metadata(args, var_type, var_name)

    return build_variable_declaration_node(args, var_name, var_type, value_id)
