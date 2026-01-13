from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.expression_statement import (
    build_expression_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    c_ids = adj_ast(args.ast_graph, args.n_id)
    ignored_types = {"await"}
    filtered_ids = [
        _id for _id in c_ids if args.ast_graph.nodes[_id]["label_type"] not in ignored_types
    ]
    return build_expression_statement_node(args, iter(filtered_ids))
