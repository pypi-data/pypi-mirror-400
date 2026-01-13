from blends.models import (
    NId,
)
from blends.syntax.builders.catch_clause import (
    build_catch_clause_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    n_attrs = args.ast_graph.nodes[args.n_id]
    block_id = n_attrs.get("label_field_body")
    param_id = n_attrs.get("label_field_name")

    return build_catch_clause_node(args, block_id, param_id)
