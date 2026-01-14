from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
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
    param_node = graph.nodes[args.n_id]

    identifier_id = param_node["label_field_name"]
    var_name = node_to_str(graph, identifier_id)

    type_id = param_node.get("label_field_type")
    var_type = node_to_str(graph, type_id) if type_id else None

    param_modifier = None
    param_modifier_id = match_ast_d(graph, args.n_id, "parameter_modifier")
    if param_modifier_id:
        param_modifier = node_to_str(graph, param_modifier_id)

    def_value = None
    equals_clause = match_ast_d(graph, args.n_id, "expression")
    if equals_clause:
        def_value = match_ast(graph, equals_clause, "=").get("__0__")

    attributes_id = match_ast_group_d(graph, args.n_id, "attribute_list")

    return build_parameter_node(
        args=args,
        variable=var_name,
        variable_type=var_type,
        value_id=def_value,
        c_ids=attributes_id,
        modifier=param_modifier,
    )
