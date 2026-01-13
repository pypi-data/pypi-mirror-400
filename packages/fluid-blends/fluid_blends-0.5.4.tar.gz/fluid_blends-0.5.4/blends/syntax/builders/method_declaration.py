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
    scope_node_attributes,
)
from blends.syntax.metadata.java import (
    add_node_range_to_method,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def _method_definition_node_id(method_node_id: NId) -> NId:
    return f"{method_node_id}__sg_def"


def _process_method_children(
    args: SyntaxGraphArgs,
    children: dict[str, list[NId]],
) -> None:
    for name_node, n_ids in children.items():
        if not n_ids:
            continue

        if name_node == "access_modifiers_n_ids":
            args.syntax_graph.nodes[args.n_id]["access_modifiers"] = " ".join(
                args.ast_graph.nodes[i].get("label_text", "") for i in n_ids
            )
            continue

        if len(n_ids) == 1:
            child_id = n_ids[0]
            args.syntax_graph.nodes[args.n_id][name_node] = child_id
            args.syntax_graph.add_edge(
                args.n_id,
                args.generic(args.fork_n_id(child_id)),
                label_ast="AST",
            )
        else:
            for child_id in n_ids:
                args.syntax_graph.add_edge(
                    args.n_id,
                    args.generic(args.fork_n_id(child_id)),
                    label_ast="AST",
                )


def build_method_declaration_node(
    args: SyntaxGraphArgs,
    name: str | None,
    block_id: NId | None,
    children: dict[str, list[NId]],
) -> NId:
    args.syntax_graph.add_node(args.n_id, label_type="MethodDeclaration")
    if name:
        args.syntax_graph.nodes[args.n_id]["name"] = name

    if ctx.has_feature_flag("StackGraph"):
        scope_stack = args.metadata.setdefault("scope_stack", [])
        if name and scope_stack and (parent_scope := scope_stack[-1]):
            method_def_id = _method_definition_node_id(args.n_id)
            args.syntax_graph.add_node(
                method_def_id,
                label_type="MethodDeclaration",
                name=name,
            )
            args.syntax_graph.update_node(
                method_def_id,
                pop_symbol_node_attributes(symbol=name, precedence=0),
            )
            add_edge(
                args.syntax_graph,
                Edge(source=parent_scope, sink=method_def_id, precedence=0),
            )
            add_edge(
                args.syntax_graph,
                Edge(source=method_def_id, sink=args.n_id, precedence=0),
            )

        args.syntax_graph.update_node(
            args.n_id,
            scope_node_attributes(is_exported=False),
        )
        if scope_stack:
            add_edge(
                args.syntax_graph,
                Edge(source=args.n_id, sink=scope_stack[-1], precedence=0),
            )
        scope_stack.append(args.n_id)

    if block_id:
        args.syntax_graph.nodes[args.n_id]["block_id"] = block_id
        args.syntax_graph.add_edge(
            args.n_id,
            args.generic(args.fork_n_id(block_id)),
            label_ast="AST",
        )

    _process_method_children(args, children)

    if args.language == Language.JAVA and args.syntax_graph.nodes.get("0") and name:
        add_node_range_to_method(args, name)

    if ctx.has_feature_flag("StackGraph"):
        scope_stack = args.metadata.setdefault("scope_stack", [])
        if scope_stack and scope_stack[-1] == args.n_id:
            scope_stack.pop()

    return args.n_id
