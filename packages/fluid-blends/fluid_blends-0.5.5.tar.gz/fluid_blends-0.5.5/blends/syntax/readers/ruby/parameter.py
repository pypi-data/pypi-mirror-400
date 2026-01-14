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
    n_attr = graph.nodes[args.n_id]

    var_name_id = n_attr.get("label_field_name")
    variable_name = (
        node_to_str(graph, var_name_id)
        if var_name_id and n_attr["label_type"] == "optional_parameter"
        else node_to_str(graph, args.n_id)
    )

    var_value_id = n_attr.get("label_field_value")

    return build_parameter_node(
        args=args,
        variable=variable_name,
        variable_type=None,
        value_id=var_value_id,
    )
