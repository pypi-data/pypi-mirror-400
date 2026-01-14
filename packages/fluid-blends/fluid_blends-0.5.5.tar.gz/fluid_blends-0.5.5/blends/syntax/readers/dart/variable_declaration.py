from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast,
    match_ast_d,
)
from blends.syntax.builders.string_literal import (
    build_string_literal_node,
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
    definition_id = match_ast_d(graph, args.n_id, "initialized_variable_definition")
    if not definition_id:
        return build_string_literal_node(args, args.n_id)

    var_type = (
        fr_child
        if (fr_child := match_ast(graph, args.n_id).get("__0__"))
        and graph.nodes[fr_child]["label_type"] == "type_identifier"
        else None
    )

    var_id = graph.nodes[definition_id]["label_field_name"]
    var_name = node_to_str(graph, var_id)

    value_id = graph.nodes[definition_id].get("label_field_value")
    if value_id and graph.nodes[value_id]["label_type"] == "identifier":
        c_ids = [
            child
            for child in adj_ast(graph, definition_id)
            if graph.nodes[child]["label_type"] == "selector"
        ]
        for c_id in c_ids:
            args.syntax_graph.add_edge(
                value_id,
                args.generic(args.fork_n_id(c_id)),
                label_ast="AST",
            )

    return build_variable_declaration_node(args, var_name, var_type, value_id)
