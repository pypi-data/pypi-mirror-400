from blends.models import (
    NId,
)
from blends.query import (
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
    text = node_to_str(graph, args.n_id)
    if text.startswith(('f"', "f'")):
        text = text.lstrip("f")
        ints = match_ast_group_d(graph, args.n_id, "interpolation")
        int_subs = [graph.nodes[_id]["label_field_expression"] for _id in ints]
        if len(int_subs) > 0:
            return build_string_literal_node(args, text, iter(int_subs))

    return build_string_literal_node(args, text)
