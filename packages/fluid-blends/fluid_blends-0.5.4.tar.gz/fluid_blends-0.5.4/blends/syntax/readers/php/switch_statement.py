from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.switch_statement import (
    build_switch_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    if (
        (value_id := args.ast_graph.nodes[args.n_id]["label_field_condition"])
        and (graph.nodes[value_id].get("label_type") == "parenthesized_expression")
        and (c_ids := match_ast(graph, value_id))
        and (clean_val := c_ids.get("__1__"))
    ):
        value_id = clean_val

    body_id = args.ast_graph.nodes[args.n_id]["label_field_body"]
    return build_switch_statement_node(args, body_id, value_id)
