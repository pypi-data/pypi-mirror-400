from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.symbol_lookup import (
    build_symbol_lookup_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    symbol_n_id = args.n_id

    if graph.nodes[args.n_id].get("label_type") == "name" and (c_ids := adj_ast(graph, args.n_id)):
        symbol_n_id = c_ids[0]

    symbol = args.ast_graph.nodes[symbol_n_id]["label_text"]

    return build_symbol_lookup_node(args, symbol)
