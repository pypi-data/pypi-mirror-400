from blends.models import (
    NId,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_annotation_node(args: SyntaxGraphArgs, attr_name: str, al_id: NId | None) -> NId:
    n_args = {
        "name": attr_name,
        "label_type": "Annotation",
    }

    if al_id:
        n_args.update(
            {
                "arguments_id": al_id,
            },
        )
    args.syntax_graph.add_node(args.n_id, **n_args)

    if al_id:
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(al_id)),
            label_ast="AST",
        )

    return args.n_id
