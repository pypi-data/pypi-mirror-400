from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
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
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    first_child, *other_childs = adj_ast(graph, args.n_id)

    if not other_childs:
        return args.generic(args.fork_n_id(first_child))

    if other_childs and (label_id := match_ast_d(graph, args.n_id, "label")):
        var_id = adj_ast(graph, label_id)[0]
        arg_name = node_to_str(graph, var_id)
        return build_named_argument_node(args, arg_name, other_childs[0])

    valid_childs = list(adj_ast(args.ast_graph, args.n_id))
    return build_argument_node(args, iter(valid_childs))
