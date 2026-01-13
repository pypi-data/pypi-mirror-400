from blends.models import (
    NId,
)
from blends.syntax.builders.named_argument import (
    build_named_argument_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    as_attrs = args.ast_graph.nodes[args.n_id]
    var_id = as_attrs["label_field_key"]
    var_name = node_to_str(args.ast_graph, var_id)
    val_id = as_attrs["label_field_value"]
    return build_named_argument_node(args, var_name, val_id)
