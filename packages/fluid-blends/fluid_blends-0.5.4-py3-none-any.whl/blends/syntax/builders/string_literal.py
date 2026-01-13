from collections.abc import (
    Iterator,
)

from blends.models import (
    NId,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_string_literal_node(
    args: SyntaxGraphArgs,
    value: str,
    c_ids: Iterator[NId] | None = None,
) -> NId:
    if value.startswith(("'", '"', "`")):
        value = value[1:-1]

    args.syntax_graph.add_node(
        args.n_id,
        value=value,
        value_type="string",
        label_type="Literal",
    )

    if c_ids:
        for c_id in c_ids:
            args.syntax_graph.add_edge(
                args.n_id,
                args.generic(args.fork_n_id(c_id)),
                label_ast="AST",
            )

    return args.n_id
