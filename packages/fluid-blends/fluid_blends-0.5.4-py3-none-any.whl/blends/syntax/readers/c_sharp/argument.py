from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
)
from blends.syntax.builders.argument import (
    build_argument_node,
)
from blends.syntax.builders.named_argument import (
    build_named_argument_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.syntax.readers.constants import (
    C_SHARP_EXPRESSION,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    match = match_ast(graph, args.n_id, ":")
    if (
        match
        and (var_id := graph.nodes[args.n_id].get("label_field_name"))
        and (val_id := match.get("__1__"))
    ):
        arg_name = node_to_str(graph, var_id)
        return build_named_argument_node(args, arg_name, val_id)

    valid_childs = [
        _id
        for _id in adj_ast(graph, args.n_id)
        if graph.nodes[_id]["label_type"] in C_SHARP_EXPRESSION.union({"declaration_expression"})
    ]

    return build_argument_node(args, iter(valid_childs))
