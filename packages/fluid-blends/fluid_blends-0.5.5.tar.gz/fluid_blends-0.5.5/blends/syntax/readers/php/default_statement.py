from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.switch_section import (
    build_switch_section_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph

    execution_ids: set[NId] = set()

    for n_id in adj_ast(graph, args.n_id)[2:]:
        if (graph.nodes[n_id].get("label_type") == "expression_statement") and (
            c_ids := adj_ast(graph, n_id)
        ):
            execution_ids.add(c_ids[0])
            continue
        execution_ids.add(n_id)

    return build_switch_section_node(args, "Default", execution_ids)
