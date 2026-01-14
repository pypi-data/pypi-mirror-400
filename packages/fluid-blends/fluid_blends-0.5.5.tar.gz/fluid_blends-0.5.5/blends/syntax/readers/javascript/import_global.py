from blends.models import (
    NId,
)
from blends.query import (
    get_node_by_path,
    match_ast_d,
    match_ast_group,
    match_ast_group_d,
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


def resolve_imports(
    args: SyntaxGraphArgs,
    expression: str,
    imports_n_ids: dict[str, list[NId]],
) -> tuple[str, str | None, set[NId]]:
    graph = args.ast_graph
    nodes = graph.nodes
    module_nodes: set[NId] = set()
    alias = None

    if (
        (namespace_n_ids := imports_n_ids.get("namespace_import"))
        and (identifier_n_id := match_ast_d(graph, namespace_n_ids[0], "identifier"))
    ) or (
        (identifier_n_ids := imports_n_ids.get("identifier"))
        and (identifier_n_id := identifier_n_ids[0])
    ):
        alias = nodes[identifier_n_id].get("label_text")

    elif (named_n_ids := imports_n_ids.get("named_imports")) and (
        specifier_n_ids := match_ast_group_d(graph, named_n_ids[0], "import_specifier")
    ):
        for specifier_n_id in specifier_n_ids:
            module_nodes.add(specifier_n_id)
            identifier_n_id = nodes[specifier_n_id].get("label_field_name")
            alias = None
    if imports_n_ids.get("identifier") and (named_n_ids := imports_n_ids.get("named_imports")):
        module_nodes.update(match_ast_group_d(graph, named_n_ids[0], "import_specifier"))
    return expression, alias, module_nodes


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    nodes = graph.nodes
    alias: str | None = None
    module_nodes: set[NId] = set()
    expression = ""

    if exp_n_id := nodes[args.n_id].get("label_field_source"):
        expression = node_to_str(graph, exp_n_id)[1:-1]
    import_clauses = match_ast_group(graph, args.n_id, "import_clause", "import_require_clause")
    clause_n_ids = import_clauses.get("import_clause") or import_clauses.get(
        "import_require_clause",
    )

    if (clause_n_ids) and (
        imports_n_ids := match_ast_group(
            graph,
            clause_n_ids[0],
            "namespace_import",
            "named_imports",
            "identifier",
        )
    ):
        expression, alias, module_nodes = resolve_imports(args, expression, imports_n_ids)
    if (import_req_n_id := import_clauses.get("import_require_clause")) and (
        exp_id := get_node_by_path(graph, import_req_n_id[0], "string", "string_fragment")
    ):
        expression = nodes[exp_id].get("label_text", "")

    return build_import_global_node(args, expression, module_nodes, alias)
