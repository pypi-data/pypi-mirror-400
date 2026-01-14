from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.object import (
    build_object_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    valid_parameters = {"class_body"}
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)
    name = ""
    for child in c_ids:
        if graph.nodes[child]["label_type"] in {
            "delegation_specifiers",
            "type_identifier",
        }:
            name = node_to_str(graph, child)
    return build_object_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"] in valid_parameters),
        name=name,
    )
