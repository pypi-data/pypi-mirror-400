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
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def _bound_import_symbol(*, expression: str, alias: str | None) -> str:
    if isinstance(alias, str) and alias:
        return alias
    parts = expression.split(".")
    return parts[-1] if parts else expression


def build_import_global_node(
    args: SyntaxGraphArgs,
    expression: str,
    module_nodes: set[NId],
    alias: str | None = None,
) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        expression=expression,
        label_type="Import",
    )

    if alias:
        args.syntax_graph.nodes[args.n_id]["label_alias"] = alias

    for node in module_nodes:
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(node)),
            label_ast="AST",
        )

    if ctx.has_feature_flag("StackGraph"):
        bound = _bound_import_symbol(expression=expression, alias=alias)
        if bound:
            args.syntax_graph.update_node(
                args.n_id,
                pop_symbol_node_attributes(symbol=bound, precedence=0),
            )
            scope_stack = args.metadata.setdefault("scope_stack", [])
            if scope_stack and (parent_scope := scope_stack[-1]):
                add_edge(
                    args.syntax_graph,
                    Edge(source=parent_scope, sink=args.n_id, precedence=0),
                )

    return args.n_id
