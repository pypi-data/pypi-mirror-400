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
    name = "AnonymousMethod"

    block_id = graph.nodes[args.n_id].get("label_field_body")

    parameters_list = graph.nodes[args.n_id].get("label_field_parameters")
    children_nid: dict[str, list[NId]] = {}
    if parameters_list is not None:
        children_nid = {
            "parameters_id": [parameters_list],
        }

    return build_method_declaration_node(args, name, block_id, children_nid)
