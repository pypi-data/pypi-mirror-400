from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.binary_operation import (
    build_binary_operation_node,
)
from blends.syntax.builders.expression_statement import (
    build_expression_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)
    invalid_childs = {";", "type_test", "(", ")"}
    expected_children_for_binary_operation = 3

    if len(c_ids) == expected_children_for_binary_operation:
        operator = node_to_str(graph, c_ids[1])
        return build_binary_operation_node(args, operator, c_ids[0], c_ids[2])

    return build_expression_statement_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"] not in invalid_childs),
    )
