from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.unary_expression import (
    build_unary_expression_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    possible_operands = {
        "member_access_expression",
        "variable_name",
        "scoped_property_access_expression",
        "subscript_expression",
    }

    operand_n_id = None
    operator_n_id = None
    childs = adj_ast(graph, args.n_id)

    for n_id in childs:
        if graph.nodes[n_id].get("label_type") in possible_operands:
            operand_n_id = n_id
        else:
            operator_n_id = n_id

    if operand_n_id and operator_n_id:
        operator = graph.nodes[operator_n_id]["label_text"]
    else:
        operand_n_id = childs[0]
        operator = childs[-1]

    return build_unary_expression_node(args, operator, operand_n_id)
