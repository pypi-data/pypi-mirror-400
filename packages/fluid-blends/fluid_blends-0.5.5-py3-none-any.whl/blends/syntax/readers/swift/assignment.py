from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.assignment import (
    build_assignment_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    as_attrs = args.ast_graph.nodes[args.n_id]
    var_id = as_attrs["label_field_target"]
    if (
        graph.nodes[var_id]["label_type"] == "directly_assignable_expression"
        and (childs := adj_ast(graph, var_id))
        and len(childs) == 1
    ):
        var_id = childs[0]
    val_id = as_attrs.get("label_field_result")
    operator_id = as_attrs.get("label_field_operator")
    operator = node_to_str(graph, operator_id) if operator_id else None
    if not val_id:
        val_id = adj_ast(graph, args.n_id)[-1]
    return build_assignment_node(args, var_id, val_id, operator)
