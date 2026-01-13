from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
)
from blends.syntax.builders.import_global import (
    build_import_global_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    expression = ""
    if identifier_n_id := match_ast_d(graph, args.n_id, "identifier"):
        expression = node_to_str(graph, identifier_n_id)
    return build_import_global_node(args, expression, set(), None)
