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
    invalid_types = {
        ";",
    }
    childs_id = adj_ast(graph, args.n_id)
    return build_expression_statement_node(
        args,
        c_ids=(c_id for c_id in childs_id if graph.nodes[c_id]["label_type"] not in invalid_types),
    )
