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
from blends.utilities.text_nodes import node_to_str


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    alias: str | None = None

    exp_n_id = match_ast_d(args.ast_graph, args.n_id, "interpreted_string_literal")
    if exp_n_id:
        expression = graph.nodes[exp_n_id].get("label_text", "")[1:-1]
    else:
        expression = node_to_str(graph, args.n_id)

    if alias_n_id := match_ast_d(args.ast_graph, args.n_id, "package_identifier"):
        alias = graph.nodes[alias_n_id].get("label_text")

    return build_import_global_node(args, expression, set(), alias)
