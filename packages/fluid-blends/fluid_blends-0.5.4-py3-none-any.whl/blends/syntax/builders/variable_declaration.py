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


def build_variable_declaration_node(  # noqa: PLR0913
    args: SyntaxGraphArgs,
    variable_name: str,
    variable_type: str | None,
    value_id: NId | None,
    var_id: NId | None = None,
    access_modifier: str | None = None,
) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        label_type="VariableDeclaration",
        variable=variable_name,
    )

    if variable_type:
        args.syntax_graph.nodes[args.n_id]["variable_type"] = variable_type

    if value_id:
        args.syntax_graph.nodes[args.n_id]["value_id"] = value_id

        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(value_id)),
            label_ast="AST",
        )
    if var_id:
        args.syntax_graph.nodes[args.n_id]["variable_id"] = var_id

        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(var_id)),
            label_ast="AST",
        )

    if access_modifier:
        args.syntax_graph.nodes[args.n_id]["access_modifier"] = access_modifier

    if ctx.has_feature_flag("StackGraph"):
        args.syntax_graph.update_node(
            args.n_id,
            pop_symbol_node_attributes(symbol=variable_name, precedence=0),
        )
        scope_stack = args.metadata.setdefault("scope_stack", [])
        if scope_stack and (parent_scope := scope_stack[-1]):
            add_edge(
                args.syntax_graph,
                Edge(source=parent_scope, sink=args.n_id, precedence=0),
            )

    return args.n_id
