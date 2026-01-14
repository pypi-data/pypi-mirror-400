from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
)
from blends.syntax.builders.parameter import (
    build_parameter_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    cp_node = graph.nodes[args.n_id]
    identifier_id = cp_node["label_field_name"]
    identifier_name = node_to_str(graph, identifier_id)
    variable_type = None
    if catch_type_id := match_ast_d(graph, args.n_id, "catch_type"):
        variable_type = node_to_str(graph, catch_type_id)

    return build_parameter_node(
        args=args,
        variable=identifier_name,
        variable_type=variable_type,
        value_id=identifier_id,
    )
