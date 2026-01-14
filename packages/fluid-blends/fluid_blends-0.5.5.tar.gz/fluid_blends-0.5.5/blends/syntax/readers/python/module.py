from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
    match_ast_group_d,
)
from blends.syntax.builders.file import (
    build_file_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    c_ids = adj_ast(graph, args.n_id)
    filtered_ids: list[NId] = []

    for _id in c_ids:
        n_attrs = graph.nodes[_id]
        if n_attrs.get("label_type") in {
            "import_statement",
            "import_from_statement",
        }:
            filtered_ids.extend(match_ast_group_d(args.ast_graph, _id, "dotted_name", depth=-1))
            if match_ast_d(graph, _id, "wildcard_import"):
                continue
            if module_n_id := n_attrs.get("label_field_module_name"):
                if module_n_id in filtered_ids:
                    filtered_ids.remove(module_n_id)
                elif d_name_n_id := match_ast_d(graph, module_n_id, "dotted_name"):
                    filtered_ids.remove(d_name_n_id)

            continue
        filtered_ids.append(_id)

    return build_file_node(args, iter(filtered_ids))
