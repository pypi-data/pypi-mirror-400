from blends.models import (
    NId,
)
from blends.query import (
    get_node_by_path,
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
    nodes = graph.nodes

    if name_n_id := get_node_by_path(
        graph,
        args.n_id,
        "property_element",
        "variable_name",
        "name",
    ):
        var_name = nodes[name_n_id].get("label_text", "")
    else:
        var_name = node_to_str(graph, args.n_id)

    val_id: NId | None = None
    if (
        val_p_id := get_node_by_path(
            graph,
            args.n_id,
            "property_element",
            "property_initializer",
        )
    ) and (c_ids := match_ast(graph, val_p_id)):
        val_id = c_ids.get("__1__")

    return build_variable_declaration_node(args, var_name, None, val_id)
