from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.class_decl import (
    build_class_node,
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
    name_id = n_attrs["label_field_name"]
    name = node_to_str(graph, name_id)

    block_id = n_attrs["label_field_body"]
    params_id = n_attrs.get("label_field_type_parameters", [])
    if params_id:
        params_id = [params_id]
        if not match_ast(graph, params_id[0], "(", ")").get("__0__"):
            params_id = []

    return build_class_node(args, name, block_id, params_id)
