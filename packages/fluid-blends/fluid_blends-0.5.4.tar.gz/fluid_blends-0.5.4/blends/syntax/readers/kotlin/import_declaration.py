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

    module_nodes: set[NId] = set()

    identifier = match_ast_d(graph, args.n_id, "qualified_identifier") or match_ast_d(
        graph,
        args.n_id,
        "identifier",
    )

    if identifier:
        expression = node_to_str(graph, identifier)

    if (alias_n_id := match_ast_d(graph, args.n_id, "import_alias")) and (
        identifier_n_id := match_ast_d(graph, alias_n_id, "type_identifier")
    ):
        alias = graph.nodes[identifier_n_id].get("label_text")

    if match_ast_d(graph, args.n_id, ".*"):
        expression += ".*"

    return build_import_global_node(args, expression, module_nodes, alias)
