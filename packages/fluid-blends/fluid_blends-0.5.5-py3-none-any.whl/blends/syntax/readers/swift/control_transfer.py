from blends.models import (
    NId,
)
from blends.syntax.builders.return_statement import (
    build_return_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    return_value = args.ast_graph.nodes[args.n_id].get("label_field_result")
    return build_return_node(args, return_value)
