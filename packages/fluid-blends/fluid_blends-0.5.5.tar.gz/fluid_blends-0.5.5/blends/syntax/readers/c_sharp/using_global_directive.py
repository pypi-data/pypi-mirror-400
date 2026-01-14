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
    nodes = graph.nodes

    name_n_id = match_ast_d(graph, args.n_id, "identifier") or match_ast_d(
        graph,
        args.n_id,
        "qualified_name",
    )
    expression = node_to_str(graph, name_n_id) if name_n_id else node_to_str(graph, args.n_id)

    alias: str | None = None
    if (alias_n_id := nodes[args.n_id].get("label_field_alias")) and (
        ident_n_id := match_ast_d(graph, alias_n_id, "identifier")
    ):
        alias = nodes[ident_n_id].get("label_text")

    return build_import_global_node(args, expression, set(), alias)
