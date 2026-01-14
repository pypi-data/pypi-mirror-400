from blends.models import (
    NId,
)
from blends.query import (
    get_ast_children,
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
    name_id = args.ast_graph.nodes[args.n_id]["label_field_name"]
    name = node_to_str(args.ast_graph, name_id)
    body_id = args.ast_graph.nodes[args.n_id]["label_field_body"]
    clause = get_ast_children(args.ast_graph, args.n_id, "extends_clause")
    var_type = None
    if clause:
        var_type = node_to_str(args.ast_graph, clause[0]).replace("extends", "")
    return build_variable_declaration_node(args, name, var_type, body_id)
