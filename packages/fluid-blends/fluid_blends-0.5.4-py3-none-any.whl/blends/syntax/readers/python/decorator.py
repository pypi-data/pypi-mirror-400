from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.modifiers import (
    build_modifiers_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    childs = adj_ast(graph, args.n_id)
    dec_ids = [childs[-1]]

    return build_modifiers_node(args, dec_ids)
