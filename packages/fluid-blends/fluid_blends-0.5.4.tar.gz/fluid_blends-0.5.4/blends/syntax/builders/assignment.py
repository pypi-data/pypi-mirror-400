from blends.ctx import ctx
from blends.models import (
    Language,
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
from blends.syntax.metadata.java import (
    del_metadata_instance,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def build_assignment_node(
    args: SyntaxGraphArgs,
    var_id: NId,
    val_id: NId,
    operator: str | None,
) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        variable_id=var_id,
        value_id=val_id,
        label_type="Assignment",
    )

    if operator:
        args.syntax_graph.nodes[args.n_id]["operator"] = operator

    args.syntax_graph.add_edge(
        args.n_id,
        args.generic(args.fork_n_id(var_id)),
        label_ast="AST",
    )

    if val_id:
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(val_id)),
            label_ast="AST",
        )

    if (args.syntax_graph.nodes.get("0")) and args.language == Language.JAVA and val_id:
        del_metadata_instance(args, var_id, val_id)

    if (
        ctx.has_feature_flag("StackGraph")
        and (symbol := bound_identifier_symbol(args, var_id=var_id)) is not None
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
