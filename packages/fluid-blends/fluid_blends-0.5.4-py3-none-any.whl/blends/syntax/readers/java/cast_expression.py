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
    type_id = n_attrs["label_field_type"]
    cast_type = node_to_str(args.ast_graph, type_id)
    val_id = n_attrs["label_field_value"]

    return build_variable_declaration_node(args, "CastExpression", cast_type, val_id)
