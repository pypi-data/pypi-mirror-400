from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.for_each_statement import (
    build_for_each_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    c_ids = adj_ast(graph, args.n_id)
    min_children_for_foreach_with_iterator = 5
    if len(c_ids) >= min_children_for_foreach_with_iterator:
        iter_item = c_ids[2]
        var_node = c_ids[4]
    else:
        iter_item = c_ids[0]
        var_node = c_ids[-1]

    body_id = graph.nodes[args.n_id].get("label_field_body")

    return build_for_each_statement_node(args, var_node, iter_item, body_id)
