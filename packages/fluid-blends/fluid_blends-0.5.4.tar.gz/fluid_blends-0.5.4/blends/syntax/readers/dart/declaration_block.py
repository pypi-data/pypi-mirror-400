from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.declaration_block import (
    build_declaration_block_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = [
        n_id
        for n_id in adj_ast(args.ast_graph, args.n_id)
        if graph.nodes[n_id]["label_type"] not in {"?", ";", "nullable_type"}
    ]
    if graph.nodes[c_ids[-1]]["label_type"] == "static_final_declaration_list":
        return args.generic(args.fork_n_id(c_ids[-1]))

    return build_declaration_block_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"]),
    )
