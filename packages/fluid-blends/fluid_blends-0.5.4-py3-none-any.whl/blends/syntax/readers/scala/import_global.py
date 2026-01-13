from blends.models import (
    NId,
)
from blends.query import (
    get_node_by_path,
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
    alias: str | None = None

    if body_id := get_node_by_path(
        graph,
        args.n_id,
        "namespace_selectors",
        "arrow_renamed_identifier",
    ):
        alias_n_id = nodes[body_id].get("label_field_alias") or ""
        alias = nodes[alias_n_id].get("label_text")
    full_import = node_to_str(graph, args.n_id)

    expression = (
        full_import.removeprefix("import").lstrip()
        if full_import.startswith("import")
        else full_import
    )

    return build_import_global_node(args, expression, set(), alias)
