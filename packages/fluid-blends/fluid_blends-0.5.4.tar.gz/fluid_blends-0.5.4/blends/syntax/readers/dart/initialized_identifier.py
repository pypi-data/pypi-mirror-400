from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
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
    c_ids = adj_ast(args.ast_graph, args.n_id)
    equalizer = match_ast_d(args.ast_graph, args.n_id, "=")
    min_children_for_variable_declaration = 3

    if len(c_ids) >= min_children_for_variable_declaration and equalizer:
        var_name = node_to_str(args.ast_graph, c_ids[0])
        return build_variable_declaration_node(args, var_name, None, c_ids[2])

    ignored_types = {"="}
    filtered_ids = [
        _id for _id in c_ids if args.ast_graph.nodes[_id]["label_type"] not in ignored_types
    ]

    return build_expression_statement_node(args, iter(filtered_ids))
