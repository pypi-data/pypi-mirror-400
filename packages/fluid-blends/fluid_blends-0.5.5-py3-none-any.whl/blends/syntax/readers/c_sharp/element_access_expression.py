from blends.models import (
    NId,
)
from blends.syntax.builders.element_access import (
    build_element_access_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    expression_id = args.ast_graph.nodes[args.n_id]["label_field_expression"]
    arguments_id = args.ast_graph.nodes[args.n_id]["label_field_subscript"]
    return build_element_access_node(args, expression_id, arguments_id)
