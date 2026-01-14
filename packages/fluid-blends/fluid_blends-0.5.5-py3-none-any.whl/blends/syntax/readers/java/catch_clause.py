from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
)
from blends.syntax.builders.catch_clause import (
    build_catch_clause_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    block = args.ast_graph.nodes[args.n_id]["label_field_body"]
    param_id = match_ast_d(args.ast_graph, args.n_id, "catch_formal_parameter")
    return build_catch_clause_node(args, block, param_id)
