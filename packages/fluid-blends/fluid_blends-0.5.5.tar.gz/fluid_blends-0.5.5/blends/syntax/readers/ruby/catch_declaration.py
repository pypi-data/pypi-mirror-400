from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
)
from blends.syntax.builders.catch_declaration import (
    build_catch_declaration_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    _, *c_ids = adj_ast(args.ast_graph, args.n_id)
    return build_catch_declaration_node(args, c_ids)
