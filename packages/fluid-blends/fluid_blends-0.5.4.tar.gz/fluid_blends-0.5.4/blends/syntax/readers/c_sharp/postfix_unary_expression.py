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
    childs = adj_ast(graph, args.n_id)
    operator = graph.nodes[childs[1]]["label_text"]
    return build_unary_expression_node(args, operator, childs[0])
