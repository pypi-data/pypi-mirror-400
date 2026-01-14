from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.do_statement import (
    build_do_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    body_id = graph.nodes[args.n_id]["label_field_body"]
    if graph.nodes[body_id]["label_type"] == "expression_statement":
        body_id = match_ast(graph, body_id)["__0__"]

    condition_node = graph.nodes[args.n_id]["label_field_condition"]

    return build_do_statement_node(args, body_id, condition_node)
