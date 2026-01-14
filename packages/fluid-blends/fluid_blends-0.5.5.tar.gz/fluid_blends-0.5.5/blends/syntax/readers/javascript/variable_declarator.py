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
    var_id = graph.nodes[args.n_id]["label_field_name"]
    var_name = node_to_str(graph, var_id)
    var_name = var_name[1:-1] if var_name.startswith("{") else var_name
    value_id = graph.nodes[args.n_id].get("label_field_value")
    return build_variable_declaration_node(args, var_name, None, value_id)
