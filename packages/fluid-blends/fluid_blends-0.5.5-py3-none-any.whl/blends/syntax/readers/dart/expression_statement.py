from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    get_ast_children,
    match_ast,
    match_ast_d,
)
from blends.syntax.builders.assignment import (
    build_assignment_node,
)
from blends.syntax.builders.expression_statement import (
    build_expression_statement_node,
)
from blends.syntax.builders.method_invocation import (
    build_method_invocation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(args.ast_graph, args.n_id)
    ignored_types = {";", "(", ")", "super", "comment"}
    filtered_ids = [
        _id for _id in c_ids if args.ast_graph.nodes[_id]["label_type"] not in ignored_types
    ]
    expected_filtered_children_for_method_invocation = 2
    if (
        len(filtered_ids) == expected_filtered_children_for_method_invocation
        and args.ast_graph.nodes[filtered_ids[0]]["label_type"] == "identifier"
        and args.ast_graph.nodes[filtered_ids[1]]["label_type"] == "selector"
        and (select_1 := match_ast_d(graph, filtered_ids[1], "argument_part"))
    ):
        expr = args.ast_graph.nodes[filtered_ids[0]]["label_text"]
        args_id = match_ast_d(graph, select_1, "arguments")
        return build_method_invocation_node(args, expr, None, args_id, None)

    expected_selectors_for_chained_method_invocation = 2
    if (
        (sel := get_ast_children(graph, args.n_id, label_type="selector"))
        and len(sel) == expected_selectors_for_chained_method_invocation
        and (select_1 := match_ast_d(graph, sel[0], "unconditional_assignable_selector"))
        and (select_2 := match_ast_d(graph, sel[1], "argument_part"))
    ):
        child_s1 = adj_ast(graph, select_1)
        expr_id = child_s1[1] if len(child_s1) > 1 else child_s1[0]
        expr = node_to_str(graph, filtered_ids[0]) + "." + node_to_str(graph, expr_id)
        args_id = match_ast_d(graph, select_2, "arguments")
        return build_method_invocation_node(
            args,
            expr,
            expr_id,
            args_id,
            {
                "object_id": filtered_ids[0],
            },
        )
    if (
        len(filtered_ids) == 1
        and args.ast_graph.nodes[filtered_ids[0]]["label_type"] == "assignment_expression"
    ):
        n_attr: dict[str, str] = graph.nodes[filtered_ids[0]]
        var_id = n_attr["label_field_left"]

        op_id = n_attr.get("label_field_operator")
        if (
            graph.nodes[var_id]["label_type"] == "assignable_expression"
            and len(adj_ast(graph, var_id)) == 1
            and (var_n_id := match_ast(graph, var_id).get("__0__"))
        ):
            var_id = var_n_id
        if op_id:
            return build_assignment_node(
                args,
                var_id,
                n_attr["label_field_right"],
                graph.nodes[op_id]["label_text"],
            )

    return build_expression_statement_node(args, iter(filtered_ids))
