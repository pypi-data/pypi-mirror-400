from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.while_statement import (
    build_while_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    block = graph.nodes[args.n_id].get("label_field_body")
    if not block:
        block = adj_ast(graph, args.n_id)[-1]
    conditional_node = graph.nodes[args.n_id]["label_field_condition"]
    return build_while_statement_node(args, block, conditional_node)
