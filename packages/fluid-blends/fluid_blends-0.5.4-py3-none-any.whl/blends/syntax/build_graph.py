from blends.ctx import ctx
from blends.models import Content, Graph, NId
from blends.stack.validation import validate_stack_graph_graph
from blends.syntax.dispatchers import DISPATCHERS_BY_LANG
from blends.syntax.models import ReaderLogicError, SyntaxGraphArgs, SyntaxMetadata
from blends.syntax.readers.common.missing_node import reader as missing_node_reader
from blends.utils.logs import log_blocking


def generic(args: SyntaxGraphArgs) -> NId:
    node_type = args.ast_graph.nodes[args.n_id]["label_type"]
    lang_dispatchers = DISPATCHERS_BY_LANG[args.language]
    if dispatcher := lang_dispatchers.get(node_type):
        try:
            return dispatcher(args)
        except ReaderLogicError as e:
            msg = f"Reader logic error for {node_type} in {args.language.name}: {e}"
            log_blocking("debug", msg)
            return missing_node_reader(args, node_type)

    msg = f"Missing syntax reader for {node_type} in {args.language.name}"
    log_blocking("debug", msg)

    return missing_node_reader(args, node_type)


def get_syntax_graph(
    ast_graph: Graph, content: Content, *, with_metadata: bool = False
) -> Graph | None:
    syntax_graph = Graph()

    syntax_metadata = SyntaxMetadata(
        class_path=[],
        scope_stack=["1"] if ctx.has_feature_flag("StackGraph") else [],
    )
    if with_metadata:
        syntax_graph.add_node(
            "0",
            label_type="Metadata",
            structure={},
            instances={},
            imports=[],
            path=str(content.path),
        )

    generic(
        SyntaxGraphArgs(
            generic,
            str(content.path),
            content.language,
            ast_graph,
            syntax_graph,
            "1",
            syntax_metadata,
        ),
    )

    if ctx.has_feature_flag("StackGraph"):
        errors = validate_stack_graph_graph(syntax_graph)
        if errors:
            max_errors = 20
            head = errors[:max_errors]
            extra = len(errors) - len(head)
            details = "; ".join(head)
            if extra > 0:
                details = f"{details}; and {extra} more"
            log_blocking(
                "warning",
                f"Stack graph validation errors in {content.path}: {details}",
            )

    return syntax_graph
