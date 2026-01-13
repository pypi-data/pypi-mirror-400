from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_group_d,
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
    value = node_to_str(graph, args.n_id)
    interpolated_ids = match_ast_group_d(graph, args.n_id, "interpolation")
    declaration_ids = (
        var_id
        for _id in interpolated_ids
        for var_id in adj_ast(graph, _id)
        if graph.nodes[var_id]["label_type"] not in {"{", "}", ",", "interpolation_brace"}
    )

    return build_string_literal_node(args, value, declaration_ids)
