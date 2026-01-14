from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
    match_ast_d,
)
from blends.syntax.builders.switch_section import (
    build_switch_section_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.syntax.readers.constants import (
    JAVA_STATEMENT,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    if (case_id := match_ast_d(graph, args.n_id, "switch_label")) and (
        case_expr_id := match_ast(graph, case_id, "case").get("__0__")
    ):
        case_expr = node_to_str(graph, case_expr_id)
    else:
        case_expr = "Default"

    execution_ids = [
        _id
        for _id in adj_ast(graph, args.n_id)
        if graph.nodes[_id]["label_type"] in JAVA_STATEMENT
        and graph.nodes[_id]["label_type"] != "break_statement"
    ]

    return build_switch_section_node(args, case_expr, execution_ids)
