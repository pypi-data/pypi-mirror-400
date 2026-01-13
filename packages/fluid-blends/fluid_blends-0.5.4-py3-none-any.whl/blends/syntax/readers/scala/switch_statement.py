from blends.models import (
    NId,
)
from blends.syntax.builders.switch_statement import (
    build_switch_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    body_id = graph.nodes[args.n_id]["label_field_body"]
    condition_id = graph.nodes[args.n_id]["label_field_value"]

    return build_switch_statement_node(args, body_id, condition_id)
