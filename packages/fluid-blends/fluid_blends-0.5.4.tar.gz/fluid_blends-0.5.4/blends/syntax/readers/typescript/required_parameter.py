from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
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
    n_attrs = args.ast_graph.nodes[args.n_id]

    pattern_id = n_attrs.get("label_field_pattern") or n_attrs.get("label_field_name")
    var_name = None
    if pattern_id:
        if args.ast_graph.nodes[pattern_id]["label_type"] == "object_pattern":
            var_name = node_to_str(args.ast_graph, pattern_id)[1:-1]
        else:
            var_name = node_to_str(args.ast_graph, pattern_id)

    type_id = n_attrs.get("label_field_type")
    var_type = None
    if type_id:
        var_type = node_to_str(args.ast_graph, type_id).replace(":", "")

    def_value = n_attrs.get("label_field_value")

    if not var_name or "," not in var_name:
        return build_parameter_node(
            args=args,
            variable=var_name,
            variable_type=var_type,
            value_id=def_value,
        )

    var_ids = (
        [
            _id
            for _id in adj_ast(args.ast_graph, pattern_id)
            if args.ast_graph.nodes[_id]["label_type"] not in {"{", "}", ","}
        ]
        if pattern_id
        else []
    )
    var_list = var_name.split(",") if var_name else []
    # As it's necessary to dynamically generate parameters in this case,
    # we have to save the last parameter as a return.
    # Otherwise, the reader will generate an extra (unnecessary) node.
    for var, var_id in zip(var_list[:-1], var_ids[:-1], strict=False):
        args.syntax_graph.add_edge(pred_ast(args.ast_graph, args.n_id)[0], var_id, label_ast="AST")
        build_parameter_node(
            args=args,
            variable=var,
            variable_type=var_type,
            value_id=def_value,
            variable_id=var_id,
        )
    return build_parameter_node(
        args=args,
        variable=var_list[-1] if len(var_list) > 1 else None,
        variable_type=var_type,
        value_id=def_value,
    )
