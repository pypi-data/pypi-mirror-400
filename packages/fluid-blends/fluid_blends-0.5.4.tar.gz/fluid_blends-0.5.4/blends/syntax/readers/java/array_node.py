from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.array_node import (
    build_array_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    childs_id = adj_ast(
        args.ast_graph,
        args.n_id,
    )

    node_types = {
        "array_initializer",
        "binary_expression",
        "cast_expression",
        "decimal_integer_literal",
        "identifier",
        "field_access",
        "object",
        "object_creation_expression",
        "string",
        "string_literal",
    }

    valid_childs = [
        child for child in childs_id if args.ast_graph.nodes[child]["label_type"] in node_types
    ]

    return build_array_node(args, valid_childs)
