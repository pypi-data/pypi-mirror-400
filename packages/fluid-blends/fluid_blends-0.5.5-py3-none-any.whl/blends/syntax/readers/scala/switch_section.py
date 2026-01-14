from blends.models import (
    NId,
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
    n_attrs = graph.nodes[args.n_id]
    case_id = n_attrs["label_field_pattern"]

    execution_ids = []
    if return_id := n_attrs.get("label_field_body"):
        execution_ids.append(return_id)

    case_expr = node_to_str(graph, case_id)
    return build_switch_section_node(args, case_expr, execution_ids)
