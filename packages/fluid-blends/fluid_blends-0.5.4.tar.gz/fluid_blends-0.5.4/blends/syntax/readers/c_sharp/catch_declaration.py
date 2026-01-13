from blends.models import (
    NId,
)
from blends.syntax.builders.parameter import (
    build_parameter_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    var_name_id = graph.nodes[args.n_id].get("label_field_name")
    variable = node_to_str(graph, var_name_id) if var_name_id else node_to_str(graph, args.n_id)

    var_type_id = graph.nodes[args.n_id].get("label_field_type")
    var_type = node_to_str(graph, var_type_id) if var_type_id else None
    return build_parameter_node(args=args, variable=variable, variable_type=var_type, value_id=None)
