from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group,
)
from blends.syntax.builders.switch_body import (
    build_switch_body_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    def_n_id: NId | None = None

    c_ids = match_ast_group(graph, args.n_id, "case_statement", "default_statement")

    case_ids = c_ids.get("case_statement", [])

    if def_n_ids := c_ids.get("default_statement"):
        def_n_id = def_n_ids[0]

    return build_switch_body_node(args, iter(case_ids), def_n_id)
