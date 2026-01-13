from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.switch_body import (
    build_switch_body_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    case_ids = match_ast_group_d(graph, args.n_id, "when_entry")
    return build_switch_body_node(args, case_ids, None)
