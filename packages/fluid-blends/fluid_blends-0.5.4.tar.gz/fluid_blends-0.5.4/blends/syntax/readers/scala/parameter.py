from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
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
    n_attrs = graph.nodes[args.n_id]
    var_type = None
    var_name = None
    c_ids = match_ast_group_d(graph, args.n_id, "annotation")

    type_id = n_attrs.get("label_field_type") or match_ast_d(graph, args.n_id, "type_identifier")
    if type_id:
        var_type = node_to_str(graph, type_id)
    identifier_id = n_attrs.get("label_field_name") or match_ast_d(graph, args.n_id, "identifier")
    if identifier_id:
        var_name = node_to_str(graph, identifier_id)

    value_id = n_attrs.get("label_field_value")
    return build_parameter_node(
        args=args,
        variable=var_name,
        variable_type=var_type,
        value_id=value_id,
        c_ids=c_ids,
    )
