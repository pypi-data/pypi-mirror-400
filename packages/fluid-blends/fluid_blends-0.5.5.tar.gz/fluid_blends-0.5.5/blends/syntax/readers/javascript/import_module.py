from blends.models import (
    NId,
)
from blends.query import (
    pred_ast,
)
from blends.syntax.builders.import_module import (
    build_import_module_node,
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
    expression = ""

    import_clauses = [
        _id
        for _id in pred_ast(graph, args.n_id, -1)
        if nodes[_id].get("label_type") == "import_statement"
    ]

    label_field_n_id = nodes[import_clauses[0]].get("label_field_source")
    if label_field_n_id:
        expression = node_to_str(graph, label_field_n_id)[1:-1]

    identifier_n_id = nodes[args.n_id].get("label_field_name") or ""
    identifier = nodes[identifier_n_id].get("label_text", "")
    expression += "." + identifier
    if alias_n_id := nodes[args.n_id].get("label_field_alias"):
        alias = nodes[alias_n_id].get("label_text")
    else:
        alias = identifier

    return build_import_module_node(args, expression, alias)
