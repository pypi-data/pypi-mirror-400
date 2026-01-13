from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.class_body import (
    build_class_body_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    _, *c_ids, _ = adj_ast(graph, args.n_id)  # do not consider { }
    return build_class_body_node(args, c_ids)
