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
    child_ids = adj_ast(graph, args.n_id)
    value_id = child_ids[0]
    case_value = node_to_str(graph, value_id) if value_id else "Default"
    body_id = child_ids[2]
    return build_switch_section_node(args, case_value, [body_id])
