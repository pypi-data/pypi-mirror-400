from blends.models import (
    NId,
)
from blends.syntax.builders.assignment import (
    build_assignment_node,
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
    variable_id = n_attrs["label_field_left"]
    value_id = n_attrs["label_field_right"]

    ruby_variable_nodes = {
        "identifier",
        "constant",
        "global_variable",
        "class_variable",
        "instance_variable",
        "exception_variable",
    }
    if graph.nodes[variable_id]["label_type"] in ruby_variable_nodes:
        var_name = node_to_str(graph, variable_id)
        return build_variable_declaration_node(args, var_name, None, value_id)

    return build_assignment_node(args, variable_id, value_id, None)
