from blends.models import (
    NId,
)
from blends.query import (
    match_ast_group_d,
)
from blends.syntax.builders.modifiers import (
    build_modifiers_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    annotation_ids = match_ast_group_d(graph, args.n_id, "annotation")
    return build_modifiers_node(args, annotation_ids)
