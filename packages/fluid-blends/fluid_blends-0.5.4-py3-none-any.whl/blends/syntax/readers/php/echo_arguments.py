from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    pred_ast,
)
from blends.syntax.builders.argument_list import (
    build_argument_list_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    invalid_types = {
        "echo",
        ",",
        ";",
    }

    nested_types = {"sequence_expression"}

    p_id = pred_ast(graph, args.n_id)[0]

    valid_childs: set[NId] = set()
    for c_id in adj_ast(args.ast_graph, p_id):
        if (label_type := graph.nodes[c_id].get("label_type")) in invalid_types:
            continue
        if label_type in nested_types:
            clean_nested_childs = [
                n_id
                for n_id in adj_ast(graph, c_id)
                if graph.nodes[n_id].get("label_type") not in invalid_types
            ]
            valid_childs.update(clean_nested_childs)
            continue
        valid_childs.add(c_id)

    return build_argument_list_node(args, iter(valid_childs))
