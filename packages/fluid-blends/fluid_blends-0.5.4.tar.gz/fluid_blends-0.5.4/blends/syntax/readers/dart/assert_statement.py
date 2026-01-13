from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.expression_statement import (
    build_expression_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    invalid_types = {
        "assertion",
        ",",
        ")",
        "(",
    }

    if (assert_exp := match_ast_d(graph, args.n_id, "assertion")) and (
        assert_args := match_ast_d(graph, assert_exp, "assertion_arguments")
    ):
        childs = [
            _id
            for _id in adj_ast(graph, assert_args)
            if graph.nodes[_id]["label_type"] not in invalid_types
        ]
        return build_expression_statement_node(args, iter(childs))

    return build_expression_statement_node(
        args,
        iter(
            [
                _id
                for _id in adj_ast(graph, args.n_id)
                if graph.nodes[_id]["label_type"] not in invalid_types
            ],
        ),
    )
