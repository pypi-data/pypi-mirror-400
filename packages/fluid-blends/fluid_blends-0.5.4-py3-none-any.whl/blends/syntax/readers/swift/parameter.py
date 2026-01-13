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
    attrs = args.ast_graph.nodes[args.n_id]

    var_id = attrs["label_field_name"]
    var_name = node_to_str(args.ast_graph, var_id)

    type_id = attrs.get("label_field_type")
    var_type = node_to_str(graph, type_id) if type_id else None

    return build_parameter_node(args=args, variable=var_name, variable_type=var_type, value_id=None)
