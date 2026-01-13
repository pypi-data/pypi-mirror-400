from collections.abc import (
    Iterator,
)

from blends.models import (
    Language,
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_execution_block_node(args: SyntaxGraphArgs, c_ids: Iterator[NId]) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        label_type="ExecutionBlock",
    )
    for c_id in c_ids:
        if (
            args.language != Language.DART
            and args.ast_graph.nodes[c_id]["label_type"] == "expression_statement"
        ):
            child_id = adj_ast(args.ast_graph, c_id)[0]
            args.syntax_graph.add_edge(
                args.n_id,
                args.generic(args.fork_n_id(child_id)),
                label_ast="AST",
            )
        else:
            args.syntax_graph.add_edge(
                args.n_id,
                args.generic(args.fork_n_id(c_id)),
                label_ast="AST",
            )

    return args.n_id
