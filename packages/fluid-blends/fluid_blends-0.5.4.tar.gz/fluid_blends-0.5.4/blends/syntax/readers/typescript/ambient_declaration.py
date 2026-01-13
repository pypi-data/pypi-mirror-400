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
    match = match_ast(graph, args.n_id, "declare")
    decl_id = match.get("__0__")
    return build_variable_declaration_node(args, "DeclareVar", None, decl_id)
