from blends.models import (
    NId,
)
from blends.query import (
    match_ast_d,
    pred_ast,
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

    expression = node_to_str(graph, args.n_id)

    for p_id in pred_ast(graph, args.n_id, depth=-1):
        if alias_n_id := nodes[p_id].get("label_field_alias"):
            alias = nodes[alias_n_id].get("label_text")
        if (module_name_n_id := nodes[p_id].get("label_field_module_name")) and (
            not match_ast_d(graph, p_id, "wildcard_import")
        ):
            module_name = node_to_str(graph, module_name_n_id)
            expression = module_name + "." + expression

    return build_import_global_node(args, expression, set(), alias)
