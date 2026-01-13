from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.php import (
    anon_method_declaration as php_anon_method_decl,
)
from blends.syntax.readers.php import (
    argument_list as php_argument_list,
)
from blends.syntax.readers.php import (
    array_creation as php_array_creation,
)
from blends.syntax.readers.php import (
    arrow as php_arrow,
)
from blends.syntax.readers.php import (
    assignment as php_assignment,
)
from blends.syntax.readers.php import (
    binary_expression as php_binary_expression,
)
from blends.syntax.readers.php import (
    boolean_literal as php_boolean_literal,
)
from blends.syntax.readers.php import (
    break_statement as php_break_statement,
)
from blends.syntax.readers.php import (
    case_statement as php_case_statement,
)
from blends.syntax.readers.php import (
    catch_clause as php_catch_clause,
)
from blends.syntax.readers.php import (
    class_declaration as php_class_declaration,
)
from blends.syntax.readers.php import (
    comment as php_comment,
)
from blends.syntax.readers.php import (
    const_declaration as php_const_declaration,
)
from blends.syntax.readers.php import (
    constant_access as php_constant_access,
)
from blends.syntax.readers.php import (
    continue_statement as php_continue_statement,
)
from blends.syntax.readers.php import (
    default_statement as php_default_statement,
)
from blends.syntax.readers.php import (
    echo_arguments as php_echo_arguments,
)
from blends.syntax.readers.php import (
    execution_block as php_execution_block,
)
from blends.syntax.readers.php import (
    expression_statement as php_expression_statement,
)
from blends.syntax.readers.php import (
    for_each_statement as php_for_each_statement,
)
from blends.syntax.readers.php import (
    for_statement as php_for_statement,
)
from blends.syntax.readers.php import (
    identifier as php_identifier,
)
from blends.syntax.readers.php import (
    if_statement as php_if_statement,
)
from blends.syntax.readers.php import (
    import_statement as php_import_statement,
)
from blends.syntax.readers.php import (
    inner_use_import as php_inner_use_import,
)
from blends.syntax.readers.php import (
    member_access as php_member_access,
)
from blends.syntax.readers.php import (
    method_declaration as php_method_declaration,
)
from blends.syntax.readers.php import (
    method_invocation as php_method_invocation,
)
from blends.syntax.readers.php import (
    namespace_definition as php_namespace_definition,
)
from blends.syntax.readers.php import (
    number_literal as php_number_literal,
)
from blends.syntax.readers.php import (
    object_creation as php_object_creation,
)
from blends.syntax.readers.php import (
    pair as php_pair,
)
from blends.syntax.readers.php import (
    parameter as php_parameter,
)
from blends.syntax.readers.php import (
    parameter_list as php_parameter_list,
)
from blends.syntax.readers.php import (
    print_statement as php_print_statement,
)
from blends.syntax.readers.php import (
    program as php_program,
)
from blends.syntax.readers.php import (
    property_access as php_property_access,
)
from blends.syntax.readers.php import (
    reserved_word as php_reserved_word,
)
from blends.syntax.readers.php import (
    return_statement as php_return_statement,
)
from blends.syntax.readers.php import (
    scoped_invocation as php_scoped_invocation,
)
from blends.syntax.readers.php import (
    string_literal as php_string_literal,
)
from blends.syntax.readers.php import (
    subscript as php_subscript,
)
from blends.syntax.readers.php import (
    switch_block as php_switch_block,
)
from blends.syntax.readers.php import (
    switch_statement as php_switch_statement,
)
from blends.syntax.readers.php import (
    text_interpolation as php_text_interpolation,
)
from blends.syntax.readers.php import (
    throw_statement as php_throw_statement,
)
from blends.syntax.readers.php import (
    try_statement as php_try_statement,
)
from blends.syntax.readers.php import (
    unary_op_expression as php_unary_operation,
)
from blends.syntax.readers.php import (
    update_expression as php_update_expression,
)
from blends.syntax.readers.php import (
    use_import as php_use_import,
)
from blends.syntax.readers.php import (
    variable_declaration as php_variable_declaration,
)
from blends.syntax.readers.php import (
    variable_name as php_variable_name,
)
from blends.syntax.readers.php import (
    while_statement as php_while_statement,
)

PHP_DISPATCHERS: Dispatcher = {
    "=>": php_arrow.reader,
    "anonymous_function_creation_expression": php_anon_method_decl.reader,
    "arguments": php_argument_list.reader,
    "array_creation_expression": php_array_creation.reader,
    "assignment_expression": php_assignment.reader,
    "augmented_assignment_expression": php_binary_expression.reader,
    "binary_expression": php_binary_expression.reader,
    "boolean": php_boolean_literal.reader,
    "break_statement": php_break_statement.reader,
    "case_statement": php_case_statement.reader,
    "catch_clause": php_catch_clause.reader,
    "class_constant_access_expression": php_constant_access.reader,
    "class_declaration": php_class_declaration.reader,
    "comment": php_comment.reader,
    "compound_statement": php_execution_block.reader,
    "const_declaration": php_const_declaration.reader,
    "continue_statement": php_continue_statement.reader,
    "declaration_list": php_execution_block.reader,
    "default_statement": php_default_statement.reader,
    "dynamic_variable_name": php_expression_statement.reader,
    "echo": php_echo_arguments.reader,
    "echo_statement": php_print_statement.reader,
    "encapsed_string": php_string_literal.reader,
    "exit_statement": php_print_statement.reader,
    "float": php_number_literal.reader,
    "foreach_statement": php_for_each_statement.reader,
    "for_statement": php_for_statement.reader,
    "formal_parameters": php_parameter_list.reader,
    "function_definition": php_method_declaration.reader,
    "function_call_expression": php_method_invocation.reader,
    "if_statement": php_if_statement.reader,
    "else_if_clause": php_if_statement.reader,
    "include_expression": php_import_statement.reader,
    "include_once_expression": php_import_statement.reader,
    "integer": php_number_literal.reader,
    "member_access_expression": php_member_access.reader,
    "member_call_expression": php_method_invocation.reader,
    "method_declaration": php_method_declaration.reader,
    "name": php_identifier.reader,
    "namespace_definition": php_namespace_definition.reader,
    "namespace_use_declaration": php_use_import.reader,
    "null": php_reserved_word.reader,
    "object_creation_expression": php_object_creation.reader,
    "pair": php_pair.reader,
    "parent": php_identifier.reader,
    "print_intrinsic": php_print_statement.reader,
    "program": php_program.reader,
    "property_declaration": php_variable_declaration.reader,
    "require_expression": php_import_statement.reader,
    "require_once_expression": php_import_statement.reader,
    "return_statement": php_return_statement.reader,
    "scoped_call_expression": php_scoped_invocation.reader,
    "scoped_property_access_expression": php_property_access.reader,
    "self": php_identifier.reader,
    "simple_parameter": php_parameter.reader,
    "string": php_string_literal.reader,
    "subscript_expression": php_subscript.reader,
    "switch_block": php_switch_block.reader,
    "switch_statement": php_switch_statement.reader,
    "text_interpolation": php_text_interpolation.reader,
    "throw_expression": php_throw_statement.reader,
    "try_statement": php_try_statement.reader,
    "unary_op_expression": php_unary_operation.reader,
    "update_expression": php_update_expression.reader,
    "use_declaration": php_inner_use_import.reader,
    "variable_name": php_variable_name.reader,
    "while_statement": php_while_statement.reader,
}
