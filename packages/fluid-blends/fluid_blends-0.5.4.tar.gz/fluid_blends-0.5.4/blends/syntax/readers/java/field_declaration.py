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
    graph = args.ast_graph
    vars_list = match_ast_group_d(graph, args.n_id, "variable_declarator")

    return build_expression_statement_node(args, iter(vars_list))
