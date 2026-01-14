from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.assignment import (
    build_assignment_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attr = graph.nodes[args.n_id]
    var_id = n_attr.get("label_field_left", "")
    val_id = n_attr.get("label_field_right", "")

    operator = None
    if op_id := n_attr.get("label_field_operator"):
        operator = graph.nodes[op_id]["label_text"]

    if (
        graph.nodes[var_id]["label_type"] == "assignable_expression"
        and len(adj_ast(graph, var_id)) == 1
        and (var_n_id := match_ast(graph, var_id).get("__0__"))
    ):
        var_id = var_n_id

    return build_assignment_node(args, var_id, val_id, operator)
