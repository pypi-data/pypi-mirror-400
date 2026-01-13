from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
)
from blends.syntax.builders.execution_block import (
    build_execution_block_node,
)
from blends.syntax.builders.string_literal import (
    build_string_literal_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)

    if (
        len(c_ids) == 1
        and (literal := match_ast_d(graph, args.n_id, "interpreted_string_literal"))
        and (value := graph.nodes[literal].get("label_text"))
    ):
        return build_string_literal_node(args, value)

    return build_execution_block_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"] not in {",", ":"}),
    )
