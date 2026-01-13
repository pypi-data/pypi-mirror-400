from blends.models import (
    NId,
)
from blends.query import (
    get_nodes_by_path,
    match_ast_group_d,
)
from blends.syntax.builders.import_statement import (
    build_import_statement_node,
)
from blends.syntax.builders.method_invocation import (
    build_method_invocation_node,
)
from blends.syntax.models import (
    SyntaxGraphArgs,
)
from blends.utilities.text_nodes import (
    node_to_str,
)


def process_ruby_imports(args: SyntaxGraphArgs, arguments_id: NId, method_name: str) -> NId:
    graph = args.ast_graph
    module_nodes: set[NId] = set()
    first_path = get_nodes_by_path(graph, arguments_id, set(), "string", "string_content")
    second_path = get_nodes_by_path(
        graph, arguments_id, set(), "string", "interpolation", "identifier"
    )
    arg = match_ast_group_d(graph, arguments_id, "identifier")
    module_nodes.update(first_path)
    module_nodes.update(second_path)
    module_nodes.update(arg)
    import_attrs: list[dict[str, str]] = []
    for module_id in module_nodes:
        module_expression = node_to_str(graph, module_id)
        import_attrs.append(
            {
                "corrected_n_id": module_id,
                "method_name": method_name,
                "expression": module_expression,
            },
        )
    return build_import_statement_node(args, *import_attrs)


def reader(args: SyntaxGraphArgs) -> NId:
    graph = args.ast_graph
    node = graph.nodes[args.n_id]

    arguments_id = node.get("label_field_arguments")
    method_id = node.get("label_field_method")
    operator_id = node.get("label_field_operator")
    object_id = node.get("label_field_receiver")
    block_id = node.get("label_field_block")

    method_name = node_to_str(graph, method_id) if method_id else ""

    if operator_id and node_to_str(graph, operator_id) == "::":
        method_name = f"::{method_name}"

    ruby_imports = {"require", "require_relative", "load", "autoload"}
    if method_name in ruby_imports and arguments_id and not object_id:
        return process_ruby_imports(args, arguments_id, method_name)

    extra_fields = {}
    if object_id:
        extra_fields["object_id"] = object_id
    if block_id:
        extra_fields["block_id"] = block_id

    return build_method_invocation_node(args, method_name, method_id, arguments_id, extra_fields)
