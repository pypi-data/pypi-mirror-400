from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.dart import (
    annotation as dart_annotation,
)
from blends.syntax.readers.dart import (
    argument as dart_argument,
)
from blends.syntax.readers.dart import (
    argument_part as dart_argument_part,
)
from blends.syntax.readers.dart import (
    arguments as dart_arguments,
)
from blends.syntax.readers.dart import (
    array_node as dart_array_node,
)
from blends.syntax.readers.dart import (
    assert_statement as dart_assert_statement,
)
from blends.syntax.readers.dart import (
    assignable_expression as dart_assignable_expression,
)
from blends.syntax.readers.dart import (
    assignable_selector as dart_assignable_selector,
)
from blends.syntax.readers.dart import (
    assignment_expression as dart_assignment_expression,
)
from blends.syntax.readers.dart import (
    await_expression as dart_await_expression,
)
from blends.syntax.readers.dart import (
    binary_expression as dart_binary_expression,
)
from blends.syntax.readers.dart import (
    boolean_literal as dart_boolean_literal,
)
from blends.syntax.readers.dart import (
    break_statement as dart_break_statement,
)
from blends.syntax.readers.dart import (
    class_body as dart_class_body,
)
from blends.syntax.readers.dart import (
    class_definition as dart_class_definition,
)
from blends.syntax.readers.dart import (
    comment as dart_comment,
)
from blends.syntax.readers.dart import (
    conditional_expression as dart_conditional_expression,
)
from blends.syntax.readers.dart import (
    constant_constructor_signature as dart_const_constructor_signature,
)
from blends.syntax.readers.dart import (
    continue_statement as dart_continue_statement,
)
from blends.syntax.readers.dart import (
    declaration_block as dart_declaration_block,
)
from blends.syntax.readers.dart import (
    enum_declaration as dart_enum_declaration,
)
from blends.syntax.readers.dart import (
    execution_block as dart_execution_block,
)
from blends.syntax.readers.dart import (
    expression_statement as dart_expression_statement,
)
from blends.syntax.readers.dart import (
    extension_declaration as dart_extension_declaration,
)
from blends.syntax.readers.dart import (
    finally_clause as dart_finally_clause,
)
from blends.syntax.readers.dart import (
    for_statement as dart_for_statement,
)
from blends.syntax.readers.dart import (
    function_body as dart_function_body,
)
from blends.syntax.readers.dart import (
    function_declaration as dart_function_declaration,
)
from blends.syntax.readers.dart import (
    function_expression as dart_function_expression,
)
from blends.syntax.readers.dart import (
    function_signature as dart_function_signature,
)
from blends.syntax.readers.dart import (
    getter_signature as dart_getter_signature,
)
from blends.syntax.readers.dart import (
    identifier as dart_identifier,
)
from blends.syntax.readers.dart import (
    identifier_list as dart_identifier_list,
)
from blends.syntax.readers.dart import (
    if_statement as dart_if_statement,
)
from blends.syntax.readers.dart import (
    import_global as dart_import_global,
)
from blends.syntax.readers.dart import (
    initialized_identifier as dart_initialized_identifier,
)
from blends.syntax.readers.dart import (
    lambda_expression as dart_lambda_expression,
)
from blends.syntax.readers.dart import (
    library_name as dart_library_name,
)
from blends.syntax.readers.dart import (
    method_declaration as dart_method_declaration,
)
from blends.syntax.readers.dart import (
    method_signature as dart_method_signature,
)
from blends.syntax.readers.dart import (
    new_expression as dart_new_expression,
)
from blends.syntax.readers.dart import (
    number_literal as dart_number_literal,
)
from blends.syntax.readers.dart import (
    object as dart_object,
)
from blends.syntax.readers.dart import (
    operator_node as dart_operator,
)
from blends.syntax.readers.dart import (
    operator_signature as dart_operator_signature,
)
from blends.syntax.readers.dart import (
    pair as dart_pair,
)
from blends.syntax.readers.dart import (
    parameter as dart_parameter,
)
from blends.syntax.readers.dart import (
    parameter_list as dart_parameter_list,
)
from blends.syntax.readers.dart import (
    parenthesized_expression as dart_parenthesized_expression,
)
from blends.syntax.readers.dart import (
    program as dart_program,
)
from blends.syntax.readers.dart import (
    reserved_word as dart_reserved_word,
)
from blends.syntax.readers.dart import (
    return_statement as dart_return_statement,
)
from blends.syntax.readers.dart import (
    selector as dart_selector,
)
from blends.syntax.readers.dart import (
    spread_element as dart_spread_element,
)
from blends.syntax.readers.dart import (
    string_literal as dart_string_literal,
)
from blends.syntax.readers.dart import (
    switch_body as dart_switch_body,
)
from blends.syntax.readers.dart import (
    switch_statement as dart_switch_statement,
)
from blends.syntax.readers.dart import (
    template_substitution as dart_template_substitution,
)
from blends.syntax.readers.dart import (
    throw_statement as dart_throw_statement,
)
from blends.syntax.readers.dart import (
    try_statement as dart_try_statement,
)
from blends.syntax.readers.dart import (
    type_cast_expression as dart_type_cast_expression,
)
from blends.syntax.readers.dart import (
    unary_expression as dart_unary_expression,
)
from blends.syntax.readers.dart import (
    update_expression as dart_update_expression,
)
from blends.syntax.readers.dart import (
    variable_declaration as dart_variable_declaration,
)
from blends.syntax.readers.dart import (
    while_statement as dart_while_statement,
)

DART_DISPATCHERS: Dispatcher = {
    "annotation": dart_annotation.reader,
    "marker_annotation": dart_annotation.reader,
    "argument": dart_argument.reader,
    "named_argument": dart_argument.reader,
    "argument_part": dart_argument_part.reader,
    "arguments": dart_arguments.reader,
    "type_arguments": dart_arguments.reader,
    "assert_statement": dart_assert_statement.reader,
    "assignable_expression": dart_assignable_expression.reader,
    "conditional_assignable_selector": dart_assignable_selector.reader,
    "unconditional_assignable_selector": dart_assignable_selector.reader,
    "assignment_expression": dart_assignment_expression.reader,
    "await_expression": dart_await_expression.reader,
    "additive_expression": dart_binary_expression.reader,
    "equality_expression": dart_binary_expression.reader,
    "logical_and_expression": dart_binary_expression.reader,
    "logical_or_expression": dart_binary_expression.reader,
    "multiplicative_expression": dart_binary_expression.reader,
    "relational_expression": dart_binary_expression.reader,
    "type_test_expression": dart_binary_expression.reader,
    "false": dart_boolean_literal.reader,
    "true": dart_boolean_literal.reader,
    "break_statement": dart_break_statement.reader,
    "class_body": dart_class_body.reader,
    "class_definition": dart_class_definition.reader,
    "comment": dart_comment.reader,
    "documentation_comment": dart_comment.reader,
    "conditional_expression": dart_conditional_expression.reader,
    "constant_constructor_signature": dart_const_constructor_signature.reader,
    "continue_statement": dart_continue_statement.reader,
    "declaration": dart_declaration_block.reader,
    "block": dart_execution_block.reader,
    "extension_body": dart_execution_block.reader,
    "enum_declaration": dart_enum_declaration.reader,
    "expression_statement": dart_expression_statement.reader,
    "extension_declaration": dart_extension_declaration.reader,
    "finally_clause": dart_finally_clause.reader,
    "for_statement": dart_for_statement.reader,
    "function_body": dart_function_body.reader,
    "function_expression_body": dart_function_body.reader,
    "function_expression": dart_function_expression.reader,
    "local_function_declaration": dart_function_declaration.reader,
    "function_signature": dart_function_signature.reader,
    "getter_signature": dart_getter_signature.reader,
    "identifier": dart_identifier.reader,
    "identifier_dollar_escaped": dart_identifier.reader,
    "initialized_identifier_list": dart_identifier_list.reader,
    "static_final_declaration_list": dart_identifier_list.reader,
    "if_statement": dart_if_statement.reader,
    "if_element": dart_if_statement.reader,
    "initialized_identifier": dart_initialized_identifier.reader,
    "static_final_declaration": dart_initialized_identifier.reader,
    "import_or_export": dart_import_global.reader,
    "lambda_expression": dart_lambda_expression.reader,
    "library_name": dart_library_name.reader,
    "constructor_signature": dart_method_declaration.reader,
    "method_signature": dart_method_signature.reader,
    "new_expression": dart_new_expression.reader,
    "decimal_floating_point_literal": dart_number_literal.reader,
    "decimal_integer_literal": dart_number_literal.reader,
    "||": dart_operator.reader,
    "&&": dart_operator.reader,
    "additive_operator": dart_operator.reader,
    "equality_operator": dart_operator.reader,
    "increment_operator": dart_operator.reader,
    "is_operator": dart_operator.reader,
    "multiplicative_operator": dart_operator.reader,
    "operator": dart_operator.reader,
    "prefix_operator": dart_operator.reader,
    "postfix_operator": dart_operator.reader,
    "relational_operator": dart_operator.reader,
    "operator_signature": dart_operator_signature.reader,
    "constructor_param": dart_parameter.reader,
    "formal_parameter": dart_parameter.reader,
    "formal_parameter_list": dart_parameter_list.reader,
    "optional_formal_parameters": dart_parameter_list.reader,
    "parenthesized_expression": dart_parenthesized_expression.reader,
    "return_statement": dart_return_statement.reader,
    "yield_statement": dart_return_statement.reader,
    "program": dart_program.reader,
    "const_builtin": dart_reserved_word.reader,
    "get": dart_reserved_word.reader,
    "inferred_type": dart_reserved_word.reader,
    "final_builtin": dart_reserved_word.reader,
    "late": dart_reserved_word.reader,
    "null_literal": dart_reserved_word.reader,
    "static": dart_reserved_word.reader,
    "sync*": dart_reserved_word.reader,
    "this": dart_reserved_word.reader,
    "type_identifier": dart_reserved_word.reader,
    "selector": dart_selector.reader,
    "list_literal": dart_string_literal.reader,
    "set_or_map_literal": dart_array_node.reader,
    "string_literal": dart_string_literal.reader,
    "switch_block": dart_switch_body.reader,
    "switch_statement": dart_switch_statement.reader,
    "template_substitution": dart_template_substitution.reader,
    "throw_expression": dart_throw_statement.reader,
    "rethrow_expression": dart_reserved_word.reader,
    "try_statement": dart_try_statement.reader,
    "type_cast_expression": dart_type_cast_expression.reader,
    "unary_expression": dart_unary_expression.reader,
    "postfix_expression": dart_update_expression.reader,
    "local_variable_declaration": dart_variable_declaration.reader,
    "do_statement": dart_while_statement.reader,
    "while_statement": dart_while_statement.reader,
    "pair": dart_pair.reader,
    "const_object_expression": dart_object.reader,
    "spread_element": dart_spread_element.reader,
}
