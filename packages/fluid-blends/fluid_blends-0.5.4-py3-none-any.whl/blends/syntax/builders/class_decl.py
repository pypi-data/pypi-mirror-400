from collections.abc import (
    Iterable,
)

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
    scope_node_attributes,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def _class_definition_node_id(class_node_id: NId) -> NId:
    return f"{class_node_id}__sg_def"


def _enter_scope_stack(args: SyntaxGraphArgs) -> None:
    if not ctx.has_feature_flag("StackGraph"):
        return
    args.syntax_graph.update_node(
        args.n_id,
        scope_node_attributes(is_exported=False),
    )
    scope_stack = args.metadata.setdefault("scope_stack", [])
    if scope_stack:
        add_edge(
            args.syntax_graph,
            Edge(source=args.n_id, sink=scope_stack[-1], precedence=0),
        )
    scope_stack.append(args.n_id)


def _exit_scope_stack_if_current(args: SyntaxGraphArgs) -> None:
    if not ctx.has_feature_flag("StackGraph"):
        return
    scope_stack = args.metadata.setdefault("scope_stack", [])
    if scope_stack and scope_stack[-1] == args.n_id:
        scope_stack.pop()


def build_class_node(  # noqa: PLR0913
    args: SyntaxGraphArgs,
    name: str,
    block_id: NId | None,
    attrl_ids: Iterable[NId] | None,
    inherited_class: str | None = None,
    modifiers_id: NId | None = None,
) -> NId:
    args.syntax_graph.add_node(
        args.n_id,
        name=name,
        block_id=block_id,
        label_type="Class",
    )

    if (
        ctx.has_feature_flag("StackGraph")
        and (scope_stack := args.metadata.setdefault("scope_stack", []))
        and (parent_scope := scope_stack[-1])
    ):
        class_def_id = _class_definition_node_id(args.n_id)
        args.syntax_graph.add_node(
            class_def_id,
            label_type="Class",
            name=name,
        )
        args.syntax_graph.update_node(
            class_def_id,
            pop_symbol_node_attributes(symbol=name, precedence=0),
        )
        add_edge(
            args.syntax_graph,
            Edge(source=parent_scope, sink=class_def_id, precedence=0),
        )
        add_edge(
            args.syntax_graph,
            Edge(source=class_def_id, sink=args.n_id, precedence=0),
        )

    _enter_scope_stack(args)

    if block_id:
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(block_id)),
            label_ast="AST",
        )

    if attrl_ids:
        for n_id in attrl_ids:
            args.syntax_graph.add_edge(
                args.n_id,
                args.generic(args.fork_n_id(n_id)),
                label_ast="AST",
            )

    if inherited_class:
        args.syntax_graph.nodes[args.n_id]["inherited_class"] = inherited_class

    if modifiers_id:
        args.syntax_graph.nodes[args.n_id]["modifiers_id"] = modifiers_id
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(modifiers_id)),
            label_ast="AST",
        )

    if args.metadata["class_path"]:
        args.metadata["class_path"].pop()

    _exit_scope_stack_if_current(args)

    return args.n_id
