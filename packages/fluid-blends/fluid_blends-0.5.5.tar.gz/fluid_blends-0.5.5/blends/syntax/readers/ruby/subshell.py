from blends.models import (
    NId,
)
from blends.query import adj_ast
from blends.syntax.builders.method_invocation import build_method_invocation_node
from blends.syntax.models import (
    SyntaxGraphArgs,
)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    arg_id = adj_ast(graph, args.n_id, label_type="string_content")[0]
    return build_method_invocation_node(
        args,
        expr="ruby_subshell_command",
        expr_id=None,
        arguments_id=arg_id,
        obj_dict=None,
    )
