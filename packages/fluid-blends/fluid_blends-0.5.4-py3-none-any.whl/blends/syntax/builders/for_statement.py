from blends.ctx import ctx
from blends.models import (
    NId,
)
from blends.stack.edges import (
    Edge,
    add_edge,
)
from blends.stack.node_helpers import (
    pop_symbol_node_attributes,
)
from blends.syntax.builders.utils import (
    bound_identifier_symbol,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_for_statement_node(
    args: SyntaxGraphArgs,
    initializer_node: NId | None,
    condition_node: NId | None,
    update_node: NId | None,
    body_node: NId,
) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        label_type="ForStatement",
        block_id=body_node,
    )

    args.syntax_graph.add_edge(
        args.n_id,
        args.generic(args.fork_n_id(body_node)),
        label_ast="AST",
    )

    if initializer_node:
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(initializer_node)),
            label_ast="AST",
        )

    if condition_node:
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(condition_node)),
            label_ast="AST",
        )

    if update_node:
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(update_node)),
            label_ast="AST",
        )

    if (
        ctx.has_feature_flag("StackGraph")
        and initializer_node is not None
        and (symbol := bound_identifier_symbol(args, var_id=initializer_node)) is not None
    ):
        args.syntax_graph.update_node(
            args.n_id,
            pop_symbol_node_attributes(symbol=symbol, precedence=0),
        )
        scope_stack = args.metadata.setdefault("scope_stack", [])
        if scope_stack and (parent_scope := scope_stack[-1]):
            add_edge(
                args.syntax_graph,
                Edge(source=parent_scope, sink=args.n_id, precedence=0),
            )

    return args.n_id
