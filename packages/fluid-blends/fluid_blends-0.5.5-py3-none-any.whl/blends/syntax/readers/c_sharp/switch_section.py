from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.switch_section import (
    build_switch_section_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.syntax.readers.constants import (
    C_SHARP_STATEMENT,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    childs = match_ast(graph, args.n_id, "case_switch_label")
    case_id = childs.get("case_switch_label")
    case_expr = node_to_str(graph, case_id) if case_id else "Default"

    execution_ids = [
        _id
        for _id in adj_ast(graph, args.n_id)
        if graph.nodes[_id]["label_type"] in C_SHARP_STATEMENT
        and graph.nodes[_id]["label_type"] != "break_statement"
    ]

    return build_switch_section_node(args, case_expr, execution_ids)
