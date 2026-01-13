from blends.models import (
    NId,
)
from blends.syntax.builders.export_statement import (
    build_export_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    expression = None
    export_block = graph.nodes[args.n_id].get("label_field_declaration")

    if export_block and graph.nodes[export_block]["label_type"] in {
        "identifier",
        "string",
    }:
        expression = node_to_str(args.ast_graph, export_block)
        export_block = None

    return build_export_statement_node(args, expression, export_block)
