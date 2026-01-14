from blends.models import (
    NId,
)
from blends.syntax.builders.import_statement import (
    build_import_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def reader(args: SyntaxGraphArgs) -> NId:
    node_attrs: dict[str, str] = {
        "expression": node_to_str(args.ast_graph, args.n_id),
    }
    return build_import_statement_node(args, node_attrs)
