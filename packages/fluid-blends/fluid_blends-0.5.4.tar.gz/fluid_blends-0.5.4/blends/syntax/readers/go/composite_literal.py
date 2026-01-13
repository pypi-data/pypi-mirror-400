from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_group_d,
)
from blends.syntax.builders.object import (
    build_object_node,
)
from blends.syntax.builders.object_creation import (
    build_object_creation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    valid_parameters = {
        "literal_value",
        "qualified_type",
    }
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)
    expected_children_for_composite_literal = 2
    if (
        len(c_ids) == expected_children_for_composite_literal
        and graph.nodes[c_ids[1]]["label_type"] == "literal_value"
        and len(match_ast_group_d(graph, c_ids[1], "keyed_element")) > 0
    ):
        name = node_to_str(graph, c_ids[0])
        if graph.nodes[c_ids[0]]["label_type"] == "map_type":
            return build_object_creation_node(
                args,
                name=name,
                arguments_id=c_ids[1],
                initializer_id=None,
            )
        return build_object_creation_node(
            args,
            name=name,
            arguments_id=c_ids[1],
            initializer_id=c_ids[0],
        )

    return build_object_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"] in valid_parameters),
    )
