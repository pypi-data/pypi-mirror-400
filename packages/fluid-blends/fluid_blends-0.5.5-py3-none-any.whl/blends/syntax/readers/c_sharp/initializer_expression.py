from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
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
    c_ids = match_ast_group_d(graph, args.n_id, "assignment_expression")

    if len(c_ids) == 0:
        children = adj_ast(graph, args.n_id)
        ignore_types = ["{", "}", ","]
        c_ids = [_id for _id in children if graph.nodes[_id]["label_type"] not in ignore_types]

    return build_expression_statement_node(args, iter(c_ids))
