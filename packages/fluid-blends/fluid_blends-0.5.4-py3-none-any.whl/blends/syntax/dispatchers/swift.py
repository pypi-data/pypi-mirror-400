from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.swift import (
    array_node as swift_array_node,
)
from blends.syntax.readers.swift import (
    as_expression as swift_as_expression,
)
from blends.syntax.readers.swift import (
    assignment as swift_assignment,
)
from blends.syntax.readers.swift import (
    availability_condition as swift_availability_condition,
)
from blends.syntax.readers.swift import (
    await_expression as swift_await_expression,
)
from blends.syntax.readers.swift import (
    binary_expression as swift_binary_expression,
)
from blends.syntax.readers.swift import (
    boolean_literal as swift_boolean_literal,
)
from blends.syntax.readers.swift import (
    call_expression as swift_call_expresion,
)
from blends.syntax.readers.swift import (
    call_suffix as swift_call_suffix,
)
from blends.syntax.readers.swift import (
    class_body as swift_class_body,
)
from blends.syntax.readers.swift import (
    class_declaration as swift_class_declaration,
)
from blends.syntax.readers.swift import (
    comment as swift_comment,
)
from blends.syntax.readers.swift import (
    control_transfer as swift_control_transfer,
)
from blends.syntax.readers.swift import (
    dictionary_literal as swift_dictionary_literal,
)
from blends.syntax.readers.swift import (
    do_statement as swift_do_statement,
)
from blends.syntax.readers.swift import (
    enum_entry as swift_enum_entry,
)
from blends.syntax.readers.swift import (
    expression_statement as swift_expression_statement,
)
from blends.syntax.readers.swift import (
    for_statement as swift_for_statement,
)
from blends.syntax.readers.swift import (
    function_body as swift_function_body,
)
from blends.syntax.readers.swift import (
    function_declaration as swift_function_declaration,
)
from blends.syntax.readers.swift import (
    identifier as swift_identifier,
)
from blends.syntax.readers.swift import (
    if_nil_expression as swift_if_nil_expression,
)
from blends.syntax.readers.swift import (
    if_statement as swift_if_statement,
)
from blends.syntax.readers.swift import (
    import_statement as swift_import_statement,
)
from blends.syntax.readers.swift import (
    integer_literal as swift_integer_literal,
)
from blends.syntax.readers.swift import (
    lambda_function as swift_lambda_function,
)
from blends.syntax.readers.swift import (
    navigation_expression as swift_navigation_expression,
)
from blends.syntax.readers.swift import (
    navigation_suffix as swift_navigation_suffix,
)
from blends.syntax.readers.swift import (
    nil as swift_nil,
)
from blends.syntax.readers.swift import (
    parameter as swift_parameter,
)
from blends.syntax.readers.swift import (
    prefix_expression as swift_prefix_expression,
)
from blends.syntax.readers.swift import (
    property_declaration as swift_property_declaration,
)
from blends.syntax.readers.swift import (
    reserved_word as swift_reserved_word,
)
from blends.syntax.readers.swift import (
    source_file as swift_source_file,
)
from blends.syntax.readers.swift import (
    statements as swift_statements,
)
from blends.syntax.readers.swift import (
    string_literal as swift_string_literal,
)
from blends.syntax.readers.swift import (
    switch_entry as swift_switch_entry,
)
from blends.syntax.readers.swift import (
    switch_statement as swift_switch_statement,
)
from blends.syntax.readers.swift import (
    ternary_expression as swift_ternary_expression,
)
from blends.syntax.readers.swift import (
    try_expression as swift_try_expression,
)
from blends.syntax.readers.swift import (
    update_expression as swift_update_expression,
)
from blends.syntax.readers.swift import (
    value_argument as swift_value_argument,
)
from blends.syntax.readers.swift import (
    value_arguments as swift_argument_list,
)
from blends.syntax.readers.swift import (
    while_statement as swift_while_statement,
)

SWIFT_DISPATCHERS: Dispatcher = {
    "lambda_literal": swift_lambda_function.reader,
    "call_suffix": swift_call_suffix.reader,
    "assignment": swift_assignment.reader,
    "availability_condition": swift_availability_condition.reader,
    "await_expression": swift_await_expression.reader,
    "value_arguments": swift_argument_list.reader,
    "additive_expression": swift_binary_expression.reader,
    "bitwise_operation": swift_binary_expression.reader,
    "comparison_expression": swift_binary_expression.reader,
    "conjunction_expression": swift_binary_expression.reader,
    "disjunction_expression": swift_binary_expression.reader,
    "equality_expression": swift_binary_expression.reader,
    "infix_expression": swift_binary_expression.reader,
    "multiplicative_expression": swift_binary_expression.reader,
    "boolean_literal": swift_boolean_literal.reader,
    "call_expression": swift_call_expresion.reader,
    "class_body": swift_class_body.reader,
    "enum_class_body": swift_class_body.reader,
    "protocol_body": swift_class_body.reader,
    "class_declaration": swift_class_declaration.reader,
    "protocol_declaration": swift_class_declaration.reader,
    "comment": swift_comment.reader,
    "directive": swift_comment.reader,
    "multiline_comment": swift_comment.reader,
    "control_transfer_statement": swift_control_transfer.reader,
    "enum_entry": swift_enum_entry.reader,
    "do_statement": swift_do_statement.reader,
    "directly_assignable_expression": swift_expression_statement.reader,
    "pattern": swift_expression_statement.reader,
    "for_statement": swift_for_statement.reader,
    "computed_property": swift_function_body.reader,
    "function_body": swift_function_body.reader,
    "function_declaration": swift_function_declaration.reader,
    "init_declaration": swift_function_declaration.reader,
    "protocol_function_declaration": swift_function_declaration.reader,
    "array_literal": swift_array_node.reader,
    "as_expression": swift_as_expression.reader,
    "constructor_expression": swift_identifier.reader,
    "identifier": swift_identifier.reader,
    "open_start_range_expression": swift_identifier.reader,
    "postfix_expression": swift_update_expression.reader,
    "self_expression": swift_identifier.reader,
    "simple_identifier": swift_identifier.reader,
    "switch_pattern": swift_identifier.reader,
    "nil_coalescing_expression": swift_if_nil_expression.reader,
    "guard_statement": swift_if_statement.reader,
    "if_statement": swift_if_statement.reader,
    "import_declaration": swift_import_statement.reader,
    "integer_literal": swift_integer_literal.reader,
    "navigation_expression": swift_navigation_expression.reader,
    "navigation_suffix": swift_navigation_suffix.reader,
    "nil": swift_nil.reader,
    "parameter": swift_parameter.reader,
    "prefix_expression": swift_prefix_expression.reader,
    "property_declaration": swift_property_declaration.reader,
    "protocol_property_declaration": swift_property_declaration.reader,
    "typealias_declaration": swift_property_declaration.reader,
    "source_file": swift_source_file.reader,
    "super_expression": swift_reserved_word.reader,
    "statements": swift_statements.reader,
    "switch_entry": swift_switch_entry.reader,
    "switch_statement": swift_switch_statement.reader,
    "dictionary_literal": swift_dictionary_literal.reader,
    "enum_type_parameters": swift_string_literal.reader,
    "line_string_literal": swift_string_literal.reader,
    "multi_line_string_literal": swift_string_literal.reader,
    "tuple_expression": swift_string_literal.reader,
    "user_type": swift_string_literal.reader,
    "ternary_expression": swift_ternary_expression.reader,
    "try_expression": swift_try_expression.reader,
    "value_argument": swift_value_argument.reader,
    "while_statement": swift_while_statement.reader,
    "repeat_while_statement": swift_while_statement.reader,
}
