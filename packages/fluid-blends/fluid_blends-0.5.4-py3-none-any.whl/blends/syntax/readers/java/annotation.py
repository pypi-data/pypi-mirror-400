from blends.models import (
    NId,
)
from blends.syntax.builders.annotation import (
    build_annotation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    annotation_id = args.ast_graph.nodes[args.n_id]["label_field_name"]
    annotation_name = node_to_str(args.ast_graph, annotation_id)
    args_id = args.ast_graph.nodes[args.n_id].get("label_field_arguments")

    return build_annotation_node(args, annotation_name, args_id)
