from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
    match_ast_d,
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
    nodes = args.ast_graph.nodes
    n_attrs = nodes[args.n_id]
    var_n_id = n_attrs["label_field_left"]
    val_n_id = n_attrs["label_field_right"]

    name_n_id = match_ast_d(args.ast_graph, var_n_id, "name", depth=-1) or ""

    if (
        nodes[val_n_id].get("label_type") == "parenthesized_expression"
        and (c_ids := match_ast(args.ast_graph, val_n_id))
        and (corrected_val := c_ids.get("__1__"))
    ):
        val_n_id = corrected_val

    var_name = nodes[name_n_id].get("label_text") or node_to_str(args.ast_graph, args.n_id)

    if nodes[var_n_id].get("label_type") == "subscript_expression":
        return build_variable_declaration_node(args, var_name, None, val_n_id, var_n_id)

    return build_variable_declaration_node(args, var_name, None, val_n_id)
