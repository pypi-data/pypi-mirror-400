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
from blends.syntax.readers.constants import (
    JAVASCRIPT_STATEMENT,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    value_id = graph.nodes[args.n_id].get("label_field_value")
    case_value = node_to_str(graph, value_id) if value_id else "Default"

    execution_ids = [
        _id
        for _id in adj_ast(graph, args.n_id)
        if graph.nodes[_id]["label_type"] in JAVASCRIPT_STATEMENT
        and graph.nodes[_id]["label_type"] != "break_statement"
    ]

    return build_switch_section_node(args, case_value, execution_ids)
