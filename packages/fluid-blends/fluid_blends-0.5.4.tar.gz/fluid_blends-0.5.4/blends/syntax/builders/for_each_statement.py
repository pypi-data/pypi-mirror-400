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


def build_for_each_statement_node(
    args: SyntaxGraphArgs,
    var_node: NId,
    iterable_item: NId,
    block_id: NId | None,
) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        iterable_item_id=iterable_item,
        variable_id=var_node,
        label_type="ForEachStatement",
    )

    args.syntax_graph.add_edge(
        args.n_id,
        args.generic(args.fork_n_id(var_node)),
        label_ast="AST",
    )

    args.syntax_graph.add_edge(
        args.n_id,
        args.generic(args.fork_n_id(iterable_item)),
        label_ast="AST",
    )
    if block_id:
        args.syntax_graph.nodes[args.n_id]["block_id"] = block_id
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(block_id)),
            label_ast="AST",
        )

    if (
        ctx.has_feature_flag("StackGraph")
        and (symbol := bound_identifier_symbol(args, var_id=var_node)) is not None
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
