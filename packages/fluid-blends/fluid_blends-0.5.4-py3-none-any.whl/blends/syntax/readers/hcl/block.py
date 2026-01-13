from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
    match_ast_group_d,
)
from blends.syntax.builders.literal import (
    build_literal_node,
)
from blends.syntax.builders.object import (
    build_object_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)

GENERATOR_DATA_SOURCES = [
    "aws_secretsmanager_random_password",
    "aws_iam_policy_document",
]


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    identifiers_id = match_ast_group_d(graph, args.n_id, "string_lit")
    name = ""
    tf_reference = None
    expected_identifiers_for_tf_reference = 2
    if len(identifiers_id) == expected_identifiers_for_tf_reference:
        name = node_to_str(graph, identifiers_id[0])[1:-1]
        reference = node_to_str(graph, identifiers_id[1])[1:-1]
        tf_reference = f"{name}.{reference}"
    elif identifier := match_ast_d(graph, args.n_id, "identifier"):
        if graph.nodes[identifier].get("label_text") == "dynamic" and len(identifiers_id) >= 1:
            name = node_to_str(graph, identifiers_id[0])[1:-1]
        else:
            name = node_to_str(graph, identifier)

    if (
        (identifier := match_ast_d(graph, args.n_id, "identifier"))
        and graph.nodes[identifier].get("label_text") == "data"
        and name not in GENERATOR_DATA_SOURCES
    ):
        return build_literal_node(args, name, "DataResource")

    if body_id := match_ast_d(graph, args.n_id, "body"):
        c_ids = adj_ast(graph, body_id)
    else:
        c_ids = adj_ast(graph, args.n_id)

    valid_parameters = {
        "attribute",
        "block",
    }

    return build_object_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"] in valid_parameters),
        name=name,
        tf_reference=tf_reference,
    )
