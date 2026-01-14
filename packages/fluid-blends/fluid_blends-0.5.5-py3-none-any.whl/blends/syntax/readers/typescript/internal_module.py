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
    var_name = "unnamed"
    childs = match_ast(args.ast_graph, args.n_id, "namespace")
    if var_id := childs.get("__0__"):
        var_name = node_to_str(args.ast_graph, var_id)

    return build_variable_declaration_node(args, var_name, None, None)
