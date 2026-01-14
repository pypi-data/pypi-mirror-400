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
    alias: str | None = None
    expression: str = ""

    if identifier := match_ast_d(graph, args.n_id, "scoped_identifier"):
        expression = node_to_str(graph, identifier)
    if match_ast_d(graph, args.n_id, "asterisk"):
        expression += ".*"
    if metadata_node := args.syntax_graph.nodes.get("0"):
        metadata_node["imports"].append(expression)

    return build_import_global_node(args, expression, set(), alias)
