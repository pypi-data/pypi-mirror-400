from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
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
    nodes = graph.nodes
    n_attrs = nodes[args.n_id]

    ignored_types = {"(", ",", ")"}

    expr_id = n_attrs.get("label_field_function") or n_attrs.get("label_field_object")
    expr = ""
    if expr_id is not None:
        if n_attrs.get("label_type") == "member_call_expression":
            raw_expr = node_to_str(graph, expr_id)
            method_name_n_id = n_attrs["label_field_name"]
            method_name = nodes[method_name_n_id].get("label_text") or node_to_str(
                graph,
                method_name_n_id,
            )
            exp_tokens = [_exp.split("(", maxsplit=1)[0] for _exp in raw_expr.split("->")]
            exp_tokens.append(method_name)
            expr = "->".join(exp_tokens)
        else:
            expr = node_to_str(graph, expr_id)

    if arguments_id := graph.nodes[args.n_id].get("label_field_arguments"):
        arguments = {
            _id
            for _id in adj_ast(graph, arguments_id)
            if graph.nodes[_id].get("label_type") not in ignored_types
        }
        if not arguments:
            arguments_id = None

    return build_method_invocation_node(args, expr, expr_id, arguments_id, None)
