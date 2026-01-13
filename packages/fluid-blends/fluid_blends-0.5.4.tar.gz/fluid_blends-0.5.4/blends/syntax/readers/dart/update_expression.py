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
    val_id = c_ids[0]

    if graph.nodes[val_id]["label_type"] == "assignable_expression":
        val_id = adj_ast(graph, val_id)[0]

    operator = graph.nodes[c_ids[1]].get("label_text", "") if len(c_ids) > 1 else "Unary"

    return build_unary_expression_node(args, operator, val_id)
