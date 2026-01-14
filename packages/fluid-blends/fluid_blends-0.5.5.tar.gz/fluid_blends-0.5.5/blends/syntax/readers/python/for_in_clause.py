from blends.models import (
    NId,
)
from blends.syntax.builders.for_each_statement import (
    build_for_each_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    node = graph.nodes[args.n_id]
    var_node = node["label_field_left"]
    iterable_item = node["label_field_right"]

    return build_for_each_statement_node(args, var_node, iterable_item, None)
