from blends.models import (
    NId,
)
from blends.query import (
    get_node_by_path,
    match_ast_d,
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
    childs = match_ast_group_d(graph, args.n_id, "jsx_opening_element") + match_ast_group_d(
        graph,
        args.n_id,
        "jsx_self_closing_element",
    )
    for _id in childs:
        jsx_attributes = match_ast_group_d(graph, _id, "jsx_attribute")
        identifier = match_ast_d(graph, _id, "identifier")
        nested_identifier = match_ast_d(graph, _id, "nested_identifier")
        spread_element = get_node_by_path(graph, _id, "jsx_expression", "spread_element")
        if jsx_attributes and len(childs) == 1:
            childs_with_attrs.extend(jsx_attributes)
        elif jsx_attributes:
            childs_with_attrs.append(_id)
        if identifier:
            childs_with_attrs.append(identifier)
        if nested_identifier:
            childs_with_attrs.append(nested_identifier)
        if spread_element:
            childs_with_attrs.append(spread_element)

    if jsx_elements_nested := match_ast_group_d(graph, args.n_id, "jsx_element"):
        childs_with_attrs.extend(jsx_elements_nested)

    return build_jsx_element_node(args, childs_with_attrs)
