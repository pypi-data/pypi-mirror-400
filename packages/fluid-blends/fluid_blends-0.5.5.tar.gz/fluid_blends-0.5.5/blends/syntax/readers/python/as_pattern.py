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


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    alias_id = graph.nodes[args.n_id].get("label_field_alias")
    children = adj_ast(graph, args.n_id)
    var_id = adj_ast(graph, alias_id)[0] if alias_id else children[-1]
    return build_assignment_node(args, var_id, children[0], None)
