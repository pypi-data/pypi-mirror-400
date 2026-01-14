from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.expression_statement import (
    build_expression_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = (
        var_id
        for var_id in adj_ast(graph, args.n_id)
        if graph.nodes[var_id]["label_type"] not in {"{", "}", ","}
    )
    return build_expression_statement_node(args, c_ids)
