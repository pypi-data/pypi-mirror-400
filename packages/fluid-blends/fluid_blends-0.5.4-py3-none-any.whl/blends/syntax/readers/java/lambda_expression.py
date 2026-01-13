from blends.models import (
    NId,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    n_attrs = args.ast_graph.nodes[args.n_id]
    body_id = n_attrs["label_field_body"]
    children = {"parameters_id": [n_attrs["label_field_parameters"]]}

    return build_method_declaration_node(args, "LambdaExpression", body_id, children)
