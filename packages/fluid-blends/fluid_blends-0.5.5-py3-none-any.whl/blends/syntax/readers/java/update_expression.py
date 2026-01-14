from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.unary_expression import (
    build_unary_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)
    exp_type = graph.nodes[c_ids[1]].get("label_text", "UpdateExpression")
    val_id = c_ids[0]

    return build_unary_expression_node(args, exp_type, val_id)
