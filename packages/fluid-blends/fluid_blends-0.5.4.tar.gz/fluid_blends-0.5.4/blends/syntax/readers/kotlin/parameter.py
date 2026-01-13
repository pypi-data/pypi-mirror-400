from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
    pred_ast,
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
    val_id = match_ast_d(graph, args.n_id, "identifier")
    var_name = node_to_str(graph, val_id) if val_id else "UnnamedParam"

    var_type_id = match_ast_d(graph, args.n_id, "user_type")
    var_type = node_to_str(graph, var_type_id) if var_type_id else None
    parent_id = pred_ast(graph, args.n_id)[0]

    parent_children = adj_ast(graph, parent_id)
    param_modifier = None

    if (
        args.n_id in parent_children
        and (idx := parent_children.index(args.n_id)) > 0
        and (prev := parent_children[idx - 1])
        and graph.nodes[prev]["label_type"] == "parameter_modifiers"
    ):
        param_modifier = node_to_str(graph, prev)

    return build_parameter_node(
        args=args,
        variable=var_name,
        variable_type=var_type,
        value_id=val_id,
        modifier=param_modifier,
    )
