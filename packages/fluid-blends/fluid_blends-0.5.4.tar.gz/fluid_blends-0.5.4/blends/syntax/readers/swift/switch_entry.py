from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.switch_section import (
    build_switch_section_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    statements_id = match_ast_d(graph, args.n_id, "statements")
    if not statements_id:
        statements_id = adj_ast(graph, args.n_id)[-1]
    child_ids = adj_ast(graph, statements_id)

    val_id = match_ast_d(graph, args.n_id, "switch_pattern")
    if not val_id:
        val_id = adj_ast(graph, args.n_id)[0]
    case_expr = node_to_str(graph, val_id)

    return build_switch_section_node(args, case_expr, child_ids)
