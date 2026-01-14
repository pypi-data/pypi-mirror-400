from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.method_declaration import (
    build_method_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    childs = adj_ast(graph, args.n_id)
    accesor_name = graph.nodes[childs[0]]["label_type"]
    block = (
        childs[1]
        if graph.nodes[childs[1]]["label_type"] in {"block", "arrow_expression_clause"}
        else None
    )
    return build_method_declaration_node(args, accesor_name, block, {})
