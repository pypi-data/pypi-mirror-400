from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.assignment import (
    build_assignment_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    n_attrs = args.ast_graph.nodes[args.n_id]
    var_id = n_attrs["label_field_body"]
    val_id = match_ast_d(args.ast_graph, args.n_id, "for_in_clause") or match_ast_d(
        args.ast_graph,
        args.n_id,
        "if_clause",
    )

    if not val_id:
        val_id = adj_ast(args.ast_graph, args.n_id)[-1]
    return build_assignment_node(args, var_id, val_id, None)
