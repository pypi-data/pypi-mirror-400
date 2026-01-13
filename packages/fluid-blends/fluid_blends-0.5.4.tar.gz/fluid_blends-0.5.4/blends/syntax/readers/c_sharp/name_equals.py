from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.expression_statement import (
    build_expression_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    var_ids = match_ast_group_d(args.ast_graph, args.n_id, "identifier")
    return build_expression_statement_node(args, iter(var_ids))
