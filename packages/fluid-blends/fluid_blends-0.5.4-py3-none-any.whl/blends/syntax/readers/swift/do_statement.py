from blends.models import (
    NId,
)
from blends.query import (
    adj_ast,
    match_ast_d,
    match_ast_group_d,
)
from blends.syntax.builders.try_statement import (
    build_try_statement_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    block_id = match_ast_d(graph, args.n_id, "statements")
    if not block_id:
        block_id = adj_ast(graph, args.n_id)[0]
    catch_id = match_ast_d(graph, args.n_id, "catch_block")
    if not catch_id:
        catch_id = adj_ast(graph, args.n_id)[-1]

    catch_statements = match_ast_group_d(graph, catch_id, "statements")
    return build_try_statement_node(args, block_id, catch_statements, None, None)
