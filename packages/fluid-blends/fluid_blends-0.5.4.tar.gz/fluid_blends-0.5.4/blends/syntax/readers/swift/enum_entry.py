from blends.models import (
    NId,
)
from blends.syntax.builders.variable_declaration import (
    build_variable_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    n_attrs = args.ast_graph.nodes[args.n_id]
    var_name = node_to_str(args.ast_graph, n_attrs["label_field_name"])
    val_id = n_attrs.get("label_field_raw_value")
    if not val_id:
        val_id = n_attrs.get("label_field_data_contents")
    return build_variable_declaration_node(args, var_name, None, val_id)
