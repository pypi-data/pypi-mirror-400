from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
    match_ast_d,
    pred_ast,
)
from blends.syntax.builders.member_access import (
    build_member_access_node,
)
from blends.syntax.builders.symbol_lookup import (
    build_symbol_lookup_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    if (
        (p_id := pred_ast(graph, args.n_id)[0])
        and (graph.nodes[p_id]["label_type"] == "member_call_expression")
        and (member_n_id := graph.nodes[p_id].get("label_field_name"))
    ):
        member = graph.nodes[member_n_id].get("label_text", "")
        expr_n_id = match_ast(graph, args.n_id).get("__1__") or args.n_id
        expression = graph.nodes[expr_n_id].get("label_text", "")
        return build_member_access_node(args, member, expression, expr_n_id)

    if name_n_id := match_ast_d(graph, args.n_id, "name"):
        symbol = graph.nodes[name_n_id].get("label_text", "")
    else:
        symbol = node_to_str(graph, args.n_id)

    return build_symbol_lookup_node(args, symbol)
