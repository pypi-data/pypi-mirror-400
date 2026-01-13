from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
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
    param_node = graph.nodes[args.n_id]
    type_id = param_node["label_field_type"]
    identifier_id = param_node["label_field_name"]

    var_type = node_to_str(graph, type_id)
    var_name = node_to_str(graph, identifier_id)

    c_ids = match_ast_group_d(graph, args.n_id, "modifiers")

    return build_parameter_node(
        args=args,
        variable=var_name,
        variable_type=var_type,
        value_id=None,
        c_ids=iter(c_ids),
    )
