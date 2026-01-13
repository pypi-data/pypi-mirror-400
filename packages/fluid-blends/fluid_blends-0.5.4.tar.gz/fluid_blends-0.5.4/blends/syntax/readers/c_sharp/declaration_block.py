from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.declaration_block import (
    build_declaration_block_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    _, *c_ids, _ = adj_ast(args.ast_graph, args.n_id)  # do not consider { }
    ignored_labels = {
        "preprocessor_call",
        "endif_directive",
        "preproc_if",
        "region_directive",
        "endregion_directive",
    }

    filtered_ids = [
        _id for _id in c_ids if args.ast_graph.nodes[_id]["label_type"] not in ignored_labels
    ]

    preproc_if_ids = [
        _id for _id in c_ids if args.ast_graph.nodes[_id]["label_type"] == "preproc_if"
    ]

    preproc_children = [
        child_id
        for n_id in preproc_if_ids
        for child_id in adj_ast(args.ast_graph, n_id)
        if args.ast_graph.nodes[child_id]["label_type"]
        not in ("#if", "parenthesized_expression", "#endif")
    ]

    return build_declaration_block_node(args, iter(filtered_ids + preproc_children))
