from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.missing_node import (
    build_missing_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs, n_type: str) -> NId:
    c_ids = adj_ast(args.ast_graph, args.n_id)

    return build_missing_node(
        args,
        n_type,
        iter(c_ids),
    )
