from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.parameter_list import (
    build_parameter_list_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    params_ids = match_ast_group_d(graph, args.n_id, "parameter")
    return build_parameter_list_node(args, params_ids)
