from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    pred_ast,
)
from blends.syntax.builders.pair import (
    build_pair_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    p_id = pred_ast(graph, args.n_id)[0]
    c_ids = [_id for _id in adj_ast(graph, p_id) if _id != args.n_id]

    key_id = c_ids[0]
    value_id = c_ids[-1]

    return build_pair_node(args, key_id, value_id)
