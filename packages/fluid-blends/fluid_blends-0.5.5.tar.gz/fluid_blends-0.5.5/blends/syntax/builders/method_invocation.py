from blends.models import (
    NId,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_method_invocation_node(
    args: SyntaxGraphArgs,
    expr: str,
    expr_id: NId | None,
    arguments_id: NId | None,
    obj_dict: dict[str, str] | None,
) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        expression=expr,
        label_type="MethodInvocation",
    )

    if obj_dict:
        if object_id := obj_dict.get("object_id"):
            args.syntax_graph.nodes[args.n_id]["object_id"] = object_id
            args.syntax_graph.add_edge(
                args.n_id,
                args.generic(args.fork_n_id(object_id)),
                label_ast="AST",
            )

        if obj_name := obj_dict.get("object"):
            args.syntax_graph.nodes[args.n_id]["object"] = obj_name

        if block_id := obj_dict.get("block_id"):
            args.syntax_graph.nodes[args.n_id]["block_id"] = block_id
            args.syntax_graph.add_edge(
                args.n_id,
                args.generic(args.fork_n_id(block_id)),
                label_ast="AST",
            )

    if expr_id:
        args.syntax_graph.nodes[args.n_id]["expression_id"] = expr_id
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(expr_id)),
            label_ast="AST",
        )

    if arguments_id:
        args.syntax_graph.nodes[args.n_id]["arguments_id"] = arguments_id
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(arguments_id)),
            label_ast="AST",
        )

    return args.n_id
