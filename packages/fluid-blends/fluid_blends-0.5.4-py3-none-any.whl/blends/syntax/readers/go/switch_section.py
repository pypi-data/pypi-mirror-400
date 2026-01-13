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
    filtered_labels = {
        "\n",
        "\r\n",
        "case",
        ":",
        "default",
    }
    childs = adj_ast(graph, args.n_id)
    value_id = graph.nodes[args.n_id].get("label_field_value") or graph.nodes[args.n_id].get(
        "label_field_type",
    )
    if not value_id:
        value_id = childs[0]
    case_expr = graph.nodes[value_id].get("label_text") or node_to_str(graph, value_id)

    execution_ids = [
        _id
        for _id in childs
        if graph.nodes[_id]["label_type"] not in filtered_labels and _id != value_id
    ]

    return build_switch_section_node(args, case_expr, iter(execution_ids))
