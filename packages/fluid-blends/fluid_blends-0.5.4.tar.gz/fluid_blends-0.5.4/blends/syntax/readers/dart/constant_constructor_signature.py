from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
)
from blends.syntax.builders.method_invocation import (
    build_method_invocation_node,
)
from blends.syntax.builders.string_literal import (
    build_string_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    if identifier_id := match_ast_d(graph, args.n_id, "identifier"):
        params_id = match_ast_d(graph, args.n_id, "formal_parameter_list")
        name = node_to_str(graph, identifier_id)
        return build_method_invocation_node(args, name, identifier_id, params_id, None)

    return build_string_literal_node(args, node_to_str(graph, args.n_id))
