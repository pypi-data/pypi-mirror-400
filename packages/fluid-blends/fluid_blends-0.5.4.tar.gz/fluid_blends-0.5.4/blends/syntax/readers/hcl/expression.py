from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.array_node import (
    build_array_node,
)
from blends.syntax.builders.method_invocation import (
    build_method_invocation_node,
)
from blends.syntax.builders.object import (
    build_object_node,
)
from blends.syntax.builders.string_literal import (
    build_string_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    child_id = adj_ast(graph, args.n_id)[0]
    if graph.nodes[child_id]["label_type"] == "collection_value":
        body_id = adj_ast(graph, child_id)[0]
        if graph.nodes[body_id]["label_type"] == "tuple":
            invalid_types = {
                "tuple_start",
                "tuple_end",
                "{",
                "}",
                ",",
                ";",
                "comment",
            }
            valid_childs = [
                child
                for child in adj_ast(graph, body_id)
                if graph.nodes[child]["label_type"] not in invalid_types
            ]
            return build_array_node(args, valid_childs)

        return build_object_node(
            args,
            c_ids=(
                _id
                for _id in adj_ast(graph, body_id)
                if graph.nodes[_id]["label_type"] in {"object_elem"}
            ),
        )

    if graph.nodes[child_id]["label_type"] == "function_call":
        expr_id = match_ast_d(graph, child_id, "identifier")
        expr = node_to_str(graph, expr_id) if expr_id else ""
        args_id = match_ast_d(graph, child_id, "function_arguments")
        return build_method_invocation_node(args, expr, expr_id, args_id, None)

    if graph.nodes[child_id]["label_type"] == "template_expr" and match_ast_d(
        graph,
        child_id,
        "heredoc_template",
    ):
        template_text = node_to_str(graph, child_id)
        try:
            start_json = template_text.index("{")
            end_json = template_text[::-1].index("}")
            return build_string_literal_node(args, template_text[start_json:-end_json])
        except ValueError:
            return build_string_literal_node(args, template_text)

    literal_text = node_to_str(graph, args.n_id)
    return build_string_literal_node(args, literal_text)
