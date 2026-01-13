from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.try_statement import (
    build_try_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    block_id = graph.nodes[args.n_id].get("label_field_expr")
    if not block_id:
        block_id = adj_ast(graph, args.n_id)[0]
    return build_try_statement_node(args, block_id, None, None, None)
