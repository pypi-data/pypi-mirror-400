from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
    match_ast_group_d,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    body_id = match_ast_d(graph, args.n_id, "switch")
    if not body_id:
        body_id = adj_ast(graph, args.n_id)[0]

    value_id = graph.nodes[args.n_id].get("label_field_initializer") or graph.nodes[args.n_id].get(
        "label_field_value",
    )

    if not value_id:
        value_id = adj_ast(graph, args.n_id)[2]

    # Go parser does not include a SwitchBody node out of the box
    args.syntax_graph.add_node(
        args.n_id,
        block_id=body_id,
        value_id=value_id,
        label_type="SwitchStatement",
    )
    args.syntax_graph.add_edge(
        args.n_id,
        body_id,
        label_ast="AST",
    )
    args.syntax_graph.add_edge(
        args.n_id,
        args.generic(args.fork_n_id(value_id)),
        label_ast="AST",
    )

    case_ids = (
        match_ast_group_d(graph, args.n_id, "expression_case")
        + match_ast_group_d(graph, args.n_id, "default_case")
        + match_ast_group_d(graph, args.n_id, "type_case")
    )

    args.syntax_graph.add_node(
        body_id,
        label_type="SwitchBody",
    )

    for c_id in case_ids:
        args.syntax_graph.add_edge(
            body_id,
            args.generic(args.fork_n_id(c_id)),
            label_ast="AST",
        )

    return args.n_id
