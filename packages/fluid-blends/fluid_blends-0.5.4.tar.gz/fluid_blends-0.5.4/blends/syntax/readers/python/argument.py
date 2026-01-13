from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
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
    childs = adj_ast(graph, args.n_id)
    n_attrs = graph.nodes[args.n_id]
    value_id = n_attrs.get("label_field_value")
    if not value_id:
        value_id = childs[-1]

    if identifier_id := n_attrs.get("label_field_name"):
        arg_name = node_to_str(graph, identifier_id)
        return build_named_argument_node(args, arg_name, value_id)

    return build_argument_node(args, iter(childs))
