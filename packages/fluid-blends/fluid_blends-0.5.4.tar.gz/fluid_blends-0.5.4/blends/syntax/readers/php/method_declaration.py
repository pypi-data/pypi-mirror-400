from blends.models import (
    NId,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes
    n_attrs = graph.nodes[args.n_id]

    name_n_id = n_attrs.get("label_field_name") or ""
    name = nodes[name_n_id].get("label_text")

    block_id = n_attrs.get("label_field_body")
    parameters_id = n_attrs.get("label_field_parameters")
    children_nid: dict[str, list[NId]] = {}
    if parameters_id is not None:
        children_nid = {
            "parameters_id": [parameters_id],
        }
    return build_method_declaration_node(args, name, block_id, children_nid)
