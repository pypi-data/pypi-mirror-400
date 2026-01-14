from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.string_literal import (
    build_string_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    value = node_to_str(graph, args.n_id)[1:-1]

    c_ids = (
        _id
        for _id in adj_ast(graph, args.n_id)
        if graph.nodes[_id].get("label_type") in {"variable_name", "subscript_expression"}
    )

    return build_string_literal_node(args, value, c_ids)
