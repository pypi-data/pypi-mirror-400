from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
    match_ast_group_d,
    search_pred_until_type,
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
    body_parents = {
        "class_body",
        "extension_body",
        "lambda_expression",
        "program",
    }
    children: dict[str, list[NId]] = {}
    body_id = None

    name_id = graph.nodes[args.n_id]["label_field_name"]
    m_name = node_to_str(graph, name_id)
    parents = search_pred_until_type(graph, args.n_id, body_parents)

    if parents and (class_childs := list(adj_ast(graph, parents[0]))):
        pm_id = match_ast_group_d(graph, args.n_id, "formal_parameter_list")
        if "__0__" in match_ast(args.ast_graph, pm_id[0], "(", ")"):
            children.update({"parameters_id": pm_id})
        body_id = class_childs[class_childs.index(parents[1]) + 1]

    return build_method_declaration_node(args, m_name, body_id, children)
