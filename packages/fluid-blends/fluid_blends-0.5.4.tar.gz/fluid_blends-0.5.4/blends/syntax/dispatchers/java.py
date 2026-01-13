from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.java import (
    annotation as java_annotation,
)
from blends.syntax.readers.java import (
    annotation_argument_list as java_annotation_argument_list,
)
from blends.syntax.readers.java import (
    argument_list as java_argument_list,
)
from blends.syntax.readers.java import (
    array_access as java_array_access,
)
from blends.syntax.readers.java import (
    array_creation_expression as java_array_creation_expression,
)
from blends.syntax.readers.java import (
    array_node as java_array,
)
from blends.syntax.readers.java import (
    assignment_expression as java_assignment_expression,
)
from blends.syntax.readers.java import (
    binary_expression as java_binary_expression,
)
from blends.syntax.readers.java import (
    boolean_literal as java_boolean_literal,
)
from blends.syntax.readers.java import (
    break_statement as java_break_statement,
)
from blends.syntax.readers.java import (
    cast_expression as java_cast_expression,
)
from blends.syntax.readers.java import (
    catch_clause as java_catch_clause,
)
from blends.syntax.readers.java import (
    catch_declaration as java_catch_declaration,
)
from blends.syntax.readers.java import (
    catch_parameter as java_catch_parameter,
)
from blends.syntax.readers.java import (
    class_body as java_class_body,
)
from blends.syntax.readers.java import (
    class_declaration as java_class_declaration,
)
from blends.syntax.readers.java import (
    comment as java_comment,
)
from blends.syntax.readers.java import (
    continue_statement as java_continue_statement,
)
from blends.syntax.readers.java import (
    declaration_block as java_declaration_block,
)
from blends.syntax.readers.java import (
    do_statement as java_do_statement,
)
from blends.syntax.readers.java import (
    element_value_pair as java_element_value_pair,
)
from blends.syntax.readers.java import (
    enhanced_for_statement as java_enhanced_for_statement,
)
from blends.syntax.readers.java import (
    execution_block as java_execution_block,
)
from blends.syntax.readers.java import (
    expression_statement as java_expression_statement,
)
from blends.syntax.readers.java import (
    field_declaration as java_field_declaration,
)
from blends.syntax.readers.java import (
    finally_clause as java_finally_clause,
)
from blends.syntax.readers.java import (
    for_statement as java_for_statement,
)
from blends.syntax.readers.java import (
    identifier as java_identifier,
)
from blends.syntax.readers.java import (
    if_statement as java_if_statement,
)
from blends.syntax.readers.java import (
    import_declaration as java_import_declaration,
)
from blends.syntax.readers.java import (
    instanceof_expression as java_instanceof_expression,
)
from blends.syntax.readers.java import (
    interface_declaration as java_interface_declaration,
)
from blends.syntax.readers.java import (
    lambda_expression as java_lambda_expression,
)
from blends.syntax.readers.java import (
    method_declaration as java_method_declaration,
)
from blends.syntax.readers.java import (
    method_invocation as java_method_invocation,
)
from blends.syntax.readers.java import (
    modifiers as java_modifiers,
)
from blends.syntax.readers.java import (
    null_literal as java_null_literal,
)
from blends.syntax.readers.java import (
    number_literal as java_number_literal,
)
from blends.syntax.readers.java import (
    object_creation_expression as java_object_creation_expression,
)
from blends.syntax.readers.java import (
    package_declaration as java_package_declaration,
)
from blends.syntax.readers.java import (
    parameter as java_parameter,
)
from blends.syntax.readers.java import (
    parameter_list as java_parameter_list,
)
from blends.syntax.readers.java import (
    parenthesized_expression as java_parenthesized_expression,
)
from blends.syntax.readers.java import (
    program as java_program,
)
from blends.syntax.readers.java import (
    resource_node as java_resource,
)
from blends.syntax.readers.java import (
    return_statement as java_return_statement,
)
from blends.syntax.readers.java import (
    string_literal as java_string_literal,
)
from blends.syntax.readers.java import (
    switch_body as java_switch_body,
)
from blends.syntax.readers.java import (
    switch_section as java_switch_section,
)
from blends.syntax.readers.java import (
    switch_statement as java_switch_statement,
)
from blends.syntax.readers.java import (
    ternary_expression as java_ternary_expression,
)
from blends.syntax.readers.java import (
    this_node as java_this,
)
from blends.syntax.readers.java import (
    throw_statement as java_throw_statement,
)
from blends.syntax.readers.java import (
    try_statement as java_try_statement,
)
from blends.syntax.readers.java import (
    unary_expression as java_unary_expression,
)
from blends.syntax.readers.java import (
    update_expression as java_update_expression,
)
from blends.syntax.readers.java import (
    variable_declaration as java_variable_declaration,
)
from blends.syntax.readers.java import (
    variable_declarator as java_variable_declarator,
)
from blends.syntax.readers.java import (
    while_statement as java_while_statement,
)

JAVA_DISPATCHERS: Dispatcher = {
    "annotation": java_annotation.reader,
    "marker_annotation": java_annotation.reader,
    "annotation_argument_list": java_annotation_argument_list.reader,
    "argument_list": java_argument_list.reader,
    "array_initializer": java_array.reader,
    "element_value_array_initializer": java_array.reader,
    "array_access": java_array_access.reader,
    "array_creation_expression": java_array_creation_expression.reader,
    "assignment_expression": java_assignment_expression.reader,
    "binary_expression": java_binary_expression.reader,
    "true": java_boolean_literal.reader,
    "false": java_boolean_literal.reader,
    "break_statement": java_break_statement.reader,
    "cast_expression": java_cast_expression.reader,
    "catch_clause": java_catch_clause.reader,
    "catch_declaration": java_catch_declaration.reader,
    "catch_formal_parameter": java_catch_parameter.reader,
    "class_body": java_class_body.reader,
    "class_literal": java_identifier.reader,
    "constructor_body": java_class_body.reader,
    "interface_body": java_class_body.reader,
    "class_declaration": java_class_declaration.reader,
    "line_comment": java_comment.reader,
    "block_comment": java_comment.reader,
    "continue_statement": java_continue_statement.reader,
    "declaration_list": java_declaration_block.reader,
    "do_statement": java_do_statement.reader,
    "block": java_execution_block.reader,
    "element_value_pair": java_element_value_pair.reader,
    "enhanced_for_statement": java_enhanced_for_statement.reader,
    "expression_statement": java_expression_statement.reader,
    "field_declaration": java_field_declaration.reader,
    "finally_clause": java_finally_clause.reader,
    "identifier": java_identifier.reader,
    "field_access": java_identifier.reader,
    "scoped_type_identifier": java_identifier.reader,
    "type_identifier": java_identifier.reader,
    "if_statement": java_if_statement.reader,
    "import_declaration": java_import_declaration.reader,
    "instanceof_expression": java_instanceof_expression.reader,
    "interface_declaration": java_interface_declaration.reader,
    "constructor_declaration": java_method_declaration.reader,
    "method_declaration": java_method_declaration.reader,
    "lambda_expression": java_lambda_expression.reader,
    "method_invocation": java_method_invocation.reader,
    "modifiers": java_modifiers.reader,
    "null_literal": java_null_literal.reader,
    "decimal_integer_literal": java_number_literal.reader,
    "integer_literal": java_number_literal.reader,
    "real_literal": java_number_literal.reader,
    "object_creation_expression": java_object_creation_expression.reader,
    "program": java_program.reader,
    "package_declaration": java_package_declaration.reader,
    "for_statement": java_for_statement.reader,
    "formal_parameter": java_parameter.reader,
    "formal_parameters": java_parameter_list.reader,
    "inferred_parameters": java_parameter_list.reader,
    "parenthesized_expression": java_parenthesized_expression.reader,
    "resource": java_resource.reader,
    "resource_specification": java_execution_block.reader,
    "return_statement": java_return_statement.reader,
    "character_literal": java_string_literal.reader,
    "string_literal": java_string_literal.reader,
    "switch_block": java_switch_body.reader,
    "switch_block_statement_group": java_switch_section.reader,
    "switch_expression": java_switch_statement.reader,
    "ternary_expression": java_ternary_expression.reader,
    "this": java_this.reader,
    "throw_statement": java_throw_statement.reader,
    "try_statement": java_try_statement.reader,
    "try_with_resources_statement": java_try_statement.reader,
    "unary_expression": java_unary_expression.reader,
    "update_expression": java_update_expression.reader,
    "constant_declaration": java_variable_declaration.reader,
    "local_variable_declaration": java_variable_declaration.reader,
    "variable_declarator": java_variable_declarator.reader,
    "while_statement": java_while_statement.reader,
}
