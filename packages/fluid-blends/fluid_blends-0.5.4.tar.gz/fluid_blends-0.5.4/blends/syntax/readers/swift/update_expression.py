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

    if (
        len(c_ids) > 1
        and graph.nodes[c_ids[1]]["label_type"] == "bang"
        and (text_id := adj_ast(graph, c_ids[1]))
    ):
        operator = graph.nodes[text_id[0]].get("label_text", "")
    else:
        operator = "Unary"

    return build_unary_expression_node(args, operator, val_id)
