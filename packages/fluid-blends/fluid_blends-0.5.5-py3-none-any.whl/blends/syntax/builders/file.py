from collections.abc import Iterable

from blends.ctx import ctx
from blends.models import (
    NId,
)
from blends.stack.node_helpers import (
    scope_node_attributes,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_file_node(args: SyntaxGraphArgs, c_ids: Iterable[NId]) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        label_type="File",
    )

    if ctx.has_feature_flag("StackGraph"):
        args.syntax_graph.update_node(
            args.n_id,
            scope_node_attributes(is_exported=True),
        )

    for c_id in c_ids:
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(c_id)),
            label_ast="AST",
        )

    return args.n_id
