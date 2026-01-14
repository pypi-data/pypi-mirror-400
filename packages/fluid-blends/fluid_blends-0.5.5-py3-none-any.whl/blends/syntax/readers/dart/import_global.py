from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
    match_ast_d,
    pred_ast,
)
from blends.syntax.builders.export_statement import (
    build_export_statement_node,
)
from blends.syntax.builders.import_global import (
    build_import_global_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes
    alias: str | None = None

    target_n_ids = match_ast(graph, args.n_id, "string_literal", "as", "library_export", depth=-1)

    exp_n_id = target_n_ids["string_literal"] or ""
    alias_n_id = target_n_ids["as"]

    expression = nodes[exp_n_id].get("label_text", "")[1:-1]

    if alias_n_id:
        p_id = pred_ast(graph, alias_n_id)[0]
        identifier_n_id = match_ast_d(graph, p_id, "identifier") or ""
        alias = nodes[identifier_n_id].get("label_text")

    if target_n_ids["library_export"]:
        return build_export_statement_node(args, expression, None)

    return build_import_global_node(args, expression, set(), alias)
