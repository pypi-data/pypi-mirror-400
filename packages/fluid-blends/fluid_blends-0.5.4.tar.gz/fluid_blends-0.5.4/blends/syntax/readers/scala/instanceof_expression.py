from blends.models import (
    NId,
)
from blends.query import (
    get_node_by_path,
)
from blends.syntax.builders.binary_operation import (
    build_binary_operation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    field_left = get_node_by_path(
        graph,
        args.n_id,
        "type_identifier",
    )

    return build_binary_operation_node(
        args,
        "isInstanceOf",
        field_left,
        None,
    )
