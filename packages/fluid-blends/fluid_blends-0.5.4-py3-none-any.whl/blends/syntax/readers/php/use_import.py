from blends.models import (
    NId,
)
from blends.query import (
    get_node_by_path,
    match_ast,
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
    expression: str = ""
    alias: str | None = None

    if (exp_n_id := match_ast_d(graph, args.n_id, "namespace_use_clause")) and (
        name_n_id := match_ast(graph, exp_n_id).get("__0__")
    ):
        expression = node_to_str(graph, name_n_id).replace("\\", "/")

        if alias_n_id := get_node_by_path(graph, exp_n_id, "namespace_aliasing_clause", "name"):
            alias = graph.nodes[alias_n_id].get("label_text")

    return build_import_global_node(args, expression, set(), alias)
