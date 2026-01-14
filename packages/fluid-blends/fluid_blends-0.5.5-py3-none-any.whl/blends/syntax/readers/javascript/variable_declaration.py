from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.expression_statement import (
    build_expression_statement_node,
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
    var_ids = match_ast_group_d(graph, args.n_id, "variable_declarator")
    if len(var_ids) == 1:
        declared_var = var_ids[0]
        var_id = graph.nodes[declared_var]["label_field_name"]
        var_name = node_to_str(graph, var_id)
        var_name = var_name[1:-1] if var_name.startswith("{") else var_name
        value_id = graph.nodes[declared_var].get("label_field_value")
        return build_variable_declaration_node(args, var_name, None, value_id)

    return build_expression_statement_node(args, iter(var_ids))
