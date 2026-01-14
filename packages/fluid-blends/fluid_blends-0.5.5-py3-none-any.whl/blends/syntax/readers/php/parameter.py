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
from blends.utilities.text_nodes import node_to_str


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]
    name_n_id = n_attrs.get("label_field_name")
    var_name = None
    if name_n_id is not None:
        name_n_id = match_ast_d(graph, name_n_id, "name") or ""
        var_name = graph.nodes[name_n_id].get("label_text", "")

    type_n_id = n_attrs.get("label_field_type")
    var_type = None
    if type_n_id is not None:
        var_type = node_to_str(graph, type_n_id)

    return build_parameter_node(args=args, variable=var_name, variable_type=var_type, value_id=None)
