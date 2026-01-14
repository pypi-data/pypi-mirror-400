from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    nodes = adj_ast(args.ast_graph, args.n_id)
    block_node = None
    if len(nodes) > 1:
        block_node = nodes[1]
    return build_method_declaration_node(args, "ArrowMethod", block_node, {})
