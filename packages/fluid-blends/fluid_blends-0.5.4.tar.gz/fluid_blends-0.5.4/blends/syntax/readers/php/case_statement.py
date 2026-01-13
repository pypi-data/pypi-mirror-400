from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
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

    case_n_id = graph.nodes[args.n_id].get("label_field_value")
    case_expr = ""
    if case_n_id is not None:
        case_expr = node_to_str(graph, case_n_id)

    if case_expr.startswith(('"', "'")):
        case_expr = case_expr[1:-1]

    execution_ids: set[NId] = set()

    for n_id in adj_ast(graph, args.n_id)[3:]:
        if (graph.nodes[n_id].get("label_type") == "expression_statement") and (
            c_ids := adj_ast(graph, n_id)
        ):
            execution_ids.add(c_ids[0])
            continue
        execution_ids.add(n_id)

    return build_switch_section_node(args, case_expr, execution_ids)
