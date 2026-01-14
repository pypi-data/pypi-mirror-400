from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
    search_pred_until_type,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    childs = adj_ast(graph, args.n_id)
    if len(childs) == 1 and graph.nodes[childs[0]]["label_type"] == "function_signature":
        return args.generic(args.fork_n_id(childs[0]))

    body_parents = {
        "class_body",
        "extension_body",
    }
    m_name = None
    children: dict[str, list[NId]] = {}
    body_id = None

    parents = search_pred_until_type(graph, args.n_id, body_parents)
    if parents and (class_childs := list(adj_ast(graph, parents[0]))):
        al_list = match_ast(graph, args.n_id, "formal_parameter_list", "static")

        parameters_id = al_list.get("formal_parameter_list")
        parameters_list = [parameters_id] if parameters_id else []

        initializers_id = al_list.get("formal_parameter_list")
        initializers_list = [initializers_id] if initializers_id else []

        children = {
            "parameters_id": parameters_list,
            "initializers": initializers_list,
        }
        body_id = class_childs[class_childs.index(parents[1]) + 1]

    return build_method_declaration_node(args, m_name, body_id, children)
