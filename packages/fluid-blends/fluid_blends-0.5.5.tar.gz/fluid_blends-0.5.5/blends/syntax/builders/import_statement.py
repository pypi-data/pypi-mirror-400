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


def _mark_import_as_definition(
    args: SyntaxGraphArgs, *, node_id: NId, expression: str, alias: str | None
) -> None:
    if not ctx.has_feature_flag("StackGraph"):
        return
    bound = _bound_import_symbol(expression=expression, alias=alias)
    if not bound:
        return
    args.syntax_graph.update_node(
        node_id,
        pop_symbol_node_attributes(symbol=bound, precedence=0),
    )
    scope_stack = args.metadata.setdefault("scope_stack", [])
    if scope_stack and (parent_scope := scope_stack[-1]):
        add_edge(
            args.syntax_graph,
            Edge(source=parent_scope, sink=node_id, precedence=0),
        )


def build_import_statement_node(args: SyntaxGraphArgs, *imported_elements: dict[str, str]) -> NId:
    if len(imported_elements) == 1:
        imported_elements[0].pop("corrected_n_id", None)
        args.syntax_graph.add_node(
            args.n_id,
            **imported_elements[0],
            label_type="Import",
        )
        expression = imported_elements[0].get("expression", "")
        alias = imported_elements[0].get("label_alias")
        _mark_import_as_definition(args, node_id=args.n_id, expression=expression, alias=alias)
    else:
        args.syntax_graph.add_node(
            args.n_id,
            import_type="multiple_import",
            label_type="Import",
        )
        for imported_element in imported_elements:
            corrected_n_id = imported_element.pop("corrected_n_id", None)
            imported_element.update({"label_type": "Import"})
            if corrected_n_id:
                args.syntax_graph.add_node(corrected_n_id, **imported_element)
                args.syntax_graph.add_edge(
                    args.n_id,
                    corrected_n_id,
                    label_ast="AST",
                )
                expression = imported_element.get("expression", "")
                alias = imported_element.get("label_alias")
                _mark_import_as_definition(
                    args,
                    node_id=corrected_n_id,
                    expression=expression,
                    alias=alias,
                )

    return args.n_id
