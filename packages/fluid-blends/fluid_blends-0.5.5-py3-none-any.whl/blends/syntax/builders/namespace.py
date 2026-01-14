from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_namespace_node(args: SyntaxGraphArgs, name: str, block_id: str | None) -> str:
    args.syntax_graph.add_node(
        args.n_id,
        name=name,
        label_type="Namespace",
    )

    if block_id:
        args.syntax_graph.nodes[args.n_id]["block_id"] = block_id
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(block_id)),
            label_ast="AST",
        )

    return args.n_id
