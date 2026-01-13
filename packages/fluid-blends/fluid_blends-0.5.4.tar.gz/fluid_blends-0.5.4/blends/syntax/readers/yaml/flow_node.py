from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.array_node import (
    build_array_node,
)
from blends.syntax.builders.literal import (
    build_literal_node,
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
    child_id = adj_ast(args.ast_graph, args.n_id)[0]
    if args.ast_graph.nodes[child_id]["label_type"] == "plain_scalar":
        lit_id = adj_ast(args.ast_graph, child_id)[0]
        literal_type = args.ast_graph.nodes[lit_id]["label_type"]
        literal_text = args.ast_graph.nodes[lit_id]["label_text"]
        if literal_type in {"integer_scalar", "float_scalar"}:
            return build_literal_node(args, literal_text, "number")
        if literal_type == "boolean_scalar":
            return build_literal_node(args, literal_text, "bool")
        if literal_type == "string_scalar":
            return build_string_literal_node(args, literal_text)

    if args.ast_graph.nodes[child_id]["label_type"] == "flow_sequence":
        valid_childs = [
            child
            for child in adj_ast(args.ast_graph, child_id)
            if args.ast_graph.nodes[child]["label_type"] not in ("[", "]", "{", "}", ",", ";")
        ]
        return build_array_node(args, valid_childs)

    text_node = node_to_str(args.ast_graph, args.n_id)
    return build_string_literal_node(args, text_node)
