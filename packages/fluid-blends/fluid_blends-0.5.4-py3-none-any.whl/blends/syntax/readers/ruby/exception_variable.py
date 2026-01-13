from blends.models import (
    NId,
)
from blends.query import (
    match_ast,
)
from blends.syntax.builders.variable_declaration import (
    build_variable_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    identifier_id = match_ast(
        graph,
        args.n_id,
        "identifier",
    )
    ident_id = identifier_id.get("identifier") or ""
    var_name = graph.nodes[ident_id]["label_text"]
    return build_variable_declaration_node(args, var_name, None, ident_id)
