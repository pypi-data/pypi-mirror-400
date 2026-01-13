from blends.models import (
    NId,
)
from blends.syntax.builders.parameter import (
    build_parameter_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    param_node = graph.nodes[args.n_id]
    type_id = param_node.get("label_field_type")
    var_type = param_node.get("label_text")
    return build_parameter_node(
        args=args,
        variable=var_type,
        variable_type=type_id,
        value_id=None,
        c_ids=None,
        modifier=None,
    )
