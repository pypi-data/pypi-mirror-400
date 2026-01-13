from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.argument_list import (
    build_argument_list_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    _, *c_ids, _ = adj_ast(graph, args.n_id)

    arg_ids = []

    for _id in c_ids:
        if graph.nodes[_id].get("label_type") == "value_argument":
            if not (graph.nodes[_id].get("label_field_name")) and (
                value_id := graph.nodes[_id].get("label_field_value")
            ):
                arg_ids.append(value_id)
            else:
                arg_ids.append(_id)

    return build_argument_list_node(
        args,
        iter(arg_ids),
    )
