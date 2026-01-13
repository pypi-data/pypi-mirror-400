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
    valid_parameters = {
        "block_mapping_pair",
        "flow_pair",
    }
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)
    return build_object_node(
        args,
        c_ids=(_id for _id in c_ids if graph.nodes[_id]["label_type"] in valid_parameters),
    )
