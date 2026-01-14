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


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    n_attrs = args.ast_graph.nodes[args.n_id]
    int_subs = match_ast_group_d(graph, args.n_id, "template_substitution")

    if len(int_subs) > 0:
        return build_string_literal_node(args, n_attrs["label_text"], iter(int_subs))
    return build_string_literal_node(args, n_attrs["label_text"])
