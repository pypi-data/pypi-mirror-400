from blends.models import (
    Graph,
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
    match_ast_d,
    match_ast_group_d,
    pred_ast,
)
from blends.syntax.builders.if_statement import (
    build_if_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def get_false_id(graph: Graph, if_n_id: NId, current_n_id: NId) -> NId | None:
    for elif_n_id in match_ast_group_d(graph, if_n_id, "else_if_clause"):
        if int(elif_n_id) > int(current_n_id):
            return elif_n_id
    if (else_n_id := match_ast_d(graph, if_n_id, "else_clause")) and (
        false_id := graph.nodes[else_n_id].get("label_field_body")
    ):
        return false_id if isinstance(false_id, str) else None
    return None


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes
    condition_id = graph.nodes[args.n_id]["label_field_condition"]

    if nodes[condition_id].get("label_type") == "parenthesized_expression":
        c_ids = match_ast(graph, condition_id)
        condition_id = c_ids.get("__1__")

    true_id = graph.nodes[args.n_id]["label_field_body"]

    if not (false_id := graph.nodes[args.n_id].get("label_field_alternative")):
        p_n_ids = pred_ast(graph, args.n_id, -1)
        for n_id in p_n_ids:
            if (nodes[n_id].get("label_type") == "if_statement") and (
                args.n_id in adj_ast(graph, n_id)
            ):
                false_id = get_false_id(graph, n_id, args.n_id)
    if false_id and nodes[false_id].get("label_type") == "else_clause":
        false_id = graph.nodes[false_id].get("label_field_body")

    return build_if_node(args, condition_id, true_id, false_id)
