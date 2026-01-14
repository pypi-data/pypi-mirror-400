from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.do_statement import (
    build_do_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.syntax.readers.constants import (
    C_SHARP_EXPRESSION,
    C_SHARP_STATEMENT,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(args.ast_graph, args.n_id)
    body_id = [_id for _id in c_ids if graph.nodes[_id]["label_type"] in C_SHARP_STATEMENT].pop()
    if graph.nodes[body_id]["label_type"] == "expression_statement":
        body_id = adj_ast(graph, body_id)[0]

    condition_node = [
        _id for _id in c_ids if graph.nodes[_id]["label_type"] in C_SHARP_EXPRESSION
    ].pop()

    return build_do_statement_node(args, body_id, condition_node)
