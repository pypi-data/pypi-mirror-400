from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.jsx_element import (
    build_jsx_element_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    childs_with_attrs = match_ast_group_d(graph, args.n_id, "jsx_attribute")
    childs_with_attrs.append(graph.nodes[args.n_id]["label_field_name"])

    return build_jsx_element_node(args, childs_with_attrs)
