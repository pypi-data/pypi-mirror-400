from blends.models import (
    NId,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_new_expression_node(
    args: SyntaxGraphArgs,
    constructor_id: NId,
    arguments_id: NId | None,
) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        constructor_id=constructor_id,
        label_type="NewExpression",
    )

    args.syntax_graph.add_edge(
        args.n_id,
        args.generic(args.fork_n_id(constructor_id)),
        label_ast="AST",
    )

    if arguments_id and args.ast_graph.nodes[arguments_id].get("label_type") != "const":
        args.syntax_graph.nodes[args.n_id]["arguments_id"] = arguments_id
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(arguments_id)),
            label_ast="AST",
        )

    return args.n_id
