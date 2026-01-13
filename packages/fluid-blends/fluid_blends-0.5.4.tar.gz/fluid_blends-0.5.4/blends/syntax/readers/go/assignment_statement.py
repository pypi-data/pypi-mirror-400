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
    as_attrs = graph.nodes[args.n_id]

    var_id = as_attrs["label_field_left"]
    if (
        graph.nodes[var_id]["label_type"] == "expression_list"
        and (childs := adj_ast(graph, var_id))
        and len(childs) == 1
    ):
        var_id = childs[0]

    val_id = as_attrs["label_field_right"]
    if (
        graph.nodes[val_id]["label_type"] == "expression_list"
        and (childs := adj_ast(graph, val_id))
        and len(childs) == 1
    ):
        val_id = childs[0]

    op_name = None
    if op_id := as_attrs.get("label_field_operator"):
        op_name = node_to_str(graph, op_id)

    return build_assignment_node(args, var_id, val_id, op_name)
