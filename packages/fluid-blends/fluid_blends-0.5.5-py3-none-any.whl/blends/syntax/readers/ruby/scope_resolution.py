from blends.models import (
    NId,
)
from blends.syntax.builders.method_invocation import (
    build_method_invocation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = graph.nodes[args.n_id]

    constant_id = n_attrs["label_field_name"]
    expression = "::" + node_to_str(graph, constant_id)

    obj_dict = {"object_id": scope_id} if (scope_id := n_attrs.get("label_field_scope")) else None

    return build_method_invocation_node(args, expression, constant_id, None, obj_dict)
