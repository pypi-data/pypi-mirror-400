from blends.models import (
    NId,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        label_type="Break",
    )
    return args.n_id
