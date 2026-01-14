from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.pair import (
    build_pair_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = [_id for _id in adj_ast(graph, args.n_id) if graph.nodes[_id].get("label_type") != "=>"]
    key_id, value_id, *_ = c_ids
    return build_pair_node(args, key_id, value_id)
