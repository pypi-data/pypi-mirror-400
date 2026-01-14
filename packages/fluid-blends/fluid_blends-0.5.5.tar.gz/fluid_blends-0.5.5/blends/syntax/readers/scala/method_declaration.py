from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]

    name = node_to_str(graph, n_attrs["label_field_name"])

    block_id = n_attrs.get("label_field_body")

    parameters_id = n_attrs.get("label_field_parameters")
    parameters_list = []
    if parameters_id and "__0__" in match_ast(graph, parameters_id, "(", ")"):
        parameters_list = [parameters_id]

    children_nid = {"parameters_id": parameters_list}

    return build_method_declaration_node(args, name, block_id, children_nid)
