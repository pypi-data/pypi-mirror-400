from blends.ctx import ctx
from blends.models import (
    NId,
)
from blends.stack.edges import (
    Edge,
    add_edge,
)
from blends.stack.node_helpers import (
    push_symbol_node_attributes,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_symbol_lookup_node(args: SyntaxGraphArgs, symbol: str) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        symbol=symbol,
        label_type="SymbolLookup",
    )

    if ctx.has_feature_flag("StackGraph"):
        args.syntax_graph.update_node(
            args.n_id,
            push_symbol_node_attributes(symbol=symbol, precedence=0),
        )
        scope_stack = args.metadata.setdefault("scope_stack", [])
        if scope_stack and (current_scope := scope_stack[-1]):
            add_edge(
                args.syntax_graph,
                Edge(source=args.n_id, sink=current_scope, precedence=0),
            )

    return args.n_id
