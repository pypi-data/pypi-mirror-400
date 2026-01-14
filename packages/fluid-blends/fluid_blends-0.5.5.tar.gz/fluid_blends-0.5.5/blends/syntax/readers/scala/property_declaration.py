from blends.models import (
    NId,
)
from blends.syntax.builders.variable_declaration import (
    build_variable_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    attrs = args.ast_graph.nodes[args.n_id]
    var_id = attrs["label_field_name"]
    val_id = attrs.get("label_field_type")
    return build_variable_declaration_node(args, var_id, None, val_id)
