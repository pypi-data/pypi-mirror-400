from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.variable_declaration import (
    build_variable_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    childs = match_ast(graph, args.n_id, "=")
    var_name = node_to_str(graph, var_id) if (var_id := childs.get("__0__")) else "UnnamedVar"

    value_id = childs.get("__1__")

    if value_id and graph.nodes[value_id]["label_type"] == "jsx_expression":
        value_id = match_ast(graph, value_id, "{").get("__0__")

    return build_variable_declaration_node(args, var_name, None, value_id)
