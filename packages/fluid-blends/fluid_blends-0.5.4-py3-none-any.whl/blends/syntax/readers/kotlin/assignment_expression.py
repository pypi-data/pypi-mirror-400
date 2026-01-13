from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.assignment import (
    build_assignment_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    children = adj_ast(graph, args.n_id)
    operator = None
    min_children_for_assignment_with_operator = 3
    if len(children) >= min_children_for_assignment_with_operator:
        var_id = children[0]
        operator = node_to_str(graph, children[1])
        val_id = children[2]
    else:
        var_id = children[0]
        val_id = children[-1]

    return build_assignment_node(args, var_id, val_id, operator)
