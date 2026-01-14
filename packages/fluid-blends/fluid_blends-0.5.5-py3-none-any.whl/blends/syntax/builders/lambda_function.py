from blends.models import NId
from blends.syntax.models import SyntaxGraphArgs


def build_lambda_function_type_node(
    args: SyntaxGraphArgs,
    param_types: list[str],
    return_type: str,
) -> NId:
    # Add the lambda_function_type node to the graph
    args.syntax_graph.add_node(
        args.n_id,
        label_type="LambdaFunctionType",
    )

    # Add parameter types as children
    for param_type in param_types:
        param_id = args.generic(args.fork_n_id(param_type))
        args.syntax_graph.add_edge(
            args.n_id,
            param_id,
            label_ast="AST",
        )

    # Add return type as a child
    return_type_id = args.generic(args.fork_n_id(return_type))
    args.syntax_graph.add_edge(
        args.n_id,
        return_type_id,
        label_ast="AST",
    )

    return args.n_id
