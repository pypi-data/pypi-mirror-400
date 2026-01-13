from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.object import (
    build_object_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)
    ignore_types = {"new", "{", "(", "}", ")", ",", "name_equals", "="}
    filtered_ids = (_id for _id in c_ids if graph.nodes[_id]["label_type"] not in ignore_types)

    return build_object_node(args, filtered_ids, "AnonymousObject")
