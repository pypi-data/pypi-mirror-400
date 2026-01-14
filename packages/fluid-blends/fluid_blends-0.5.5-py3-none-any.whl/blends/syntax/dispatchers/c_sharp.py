from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.c_sharp import (
    accessor_declaration as cs_accessor_declaration,
)
from blends.syntax.readers.c_sharp import (
    anonymous_object_creation as cs_anon_object_creation,
)
from blends.syntax.readers.c_sharp import (
    argument as cs_argument,
)
from blends.syntax.readers.c_sharp import (
    argument_list as cs_argument_list,
)
from blends.syntax.readers.c_sharp import (
    array_creation_expression as cs_array_creation_expression,
)
from blends.syntax.readers.c_sharp import (
    arrow_expression_clause as cs_arrow_expression_clause,
)
from blends.syntax.readers.c_sharp import (
    assignment_expression as cs_assignment_expression,
)
from blends.syntax.readers.c_sharp import (
    attribute as cs_attribute,
)
from blends.syntax.readers.c_sharp import (
    attribute_list as cs_attribute_list,
)
from blends.syntax.readers.c_sharp import (
    binary_expression as cs_binary_expression,
)
from blends.syntax.readers.c_sharp import (
    boolean_literal as cs_boolean_literal,
)
from blends.syntax.readers.c_sharp import (
    bracketed_argument_list as cs_bracketed_argument_list,
)
from blends.syntax.readers.c_sharp import (
    break_statement as cs_break_statement,
)
from blends.syntax.readers.c_sharp import (
    cast_expression as cs_cast_expression,
)
from blends.syntax.readers.c_sharp import (
    catch_clause as cs_catch_clause,
)
from blends.syntax.readers.c_sharp import (
    catch_declaration as cs_catch_declaration,
)
from blends.syntax.readers.c_sharp import (
    class_declaration as cs_class_declaration,
)
from blends.syntax.readers.c_sharp import (
    comment as cs_comment,
)
from blends.syntax.readers.c_sharp import (
    compilation_unit as cs_compilation_unit,
)
from blends.syntax.readers.c_sharp import (
    conditional_access_expression as cs_conditional_access_expression,
)
from blends.syntax.readers.c_sharp import (
    constructor_declaration as cs_constructor_declaration,
)
from blends.syntax.readers.c_sharp import (
    continue_statement as cs_continue_statement,
)
from blends.syntax.readers.c_sharp import (
    declaration_block as cs_declaration_block,
)
from blends.syntax.readers.c_sharp import (
    do_statement as cs_do_statement,
)
from blends.syntax.readers.c_sharp import (
    element_access_expression as cs_element_access_expression,
)
from blends.syntax.readers.c_sharp import (
    element_binding_expression as cs_element_binding_expression,
)
from blends.syntax.readers.c_sharp import (
    execution_block as cs_execution_block,
)
from blends.syntax.readers.c_sharp import (
    expression_statement as cs_expression_statement,
)
from blends.syntax.readers.c_sharp import (
    file_scoped_namespace_declaration as cs_file_scoped_namespace_decla,
)
from blends.syntax.readers.c_sharp import (
    finally_clause as cs_finally_clause,
)
from blends.syntax.readers.c_sharp import (
    for_each_statement as cs_for_each_statement,
)
from blends.syntax.readers.c_sharp import (
    for_statement as cs_for_statement,
)
from blends.syntax.readers.c_sharp import (
    global_statement as cs_global_statement,
)
from blends.syntax.readers.c_sharp import (
    identifier as cs_identifier,
)
from blends.syntax.readers.c_sharp import (
    if_statement as cs_if_statement,
)
from blends.syntax.readers.c_sharp import (
    implicit_parameter as cs_implicit_parameter,
)
from blends.syntax.readers.c_sharp import (
    initializer_expression as cs_initializer_expression,
)
from blends.syntax.readers.c_sharp import (
    interface_declaration as cs_interface_declaration,
)
from blends.syntax.readers.c_sharp import (
    interpolated_string_expression as cs_interpolated_string_expression,
)
from blends.syntax.readers.c_sharp import (
    interpolation as cs_interpolation,
)
from blends.syntax.readers.c_sharp import (
    invocation_expression as cs_invocation_expression,
)
from blends.syntax.readers.c_sharp import (
    lambda_expression as cs_lambda_expression,
)
from blends.syntax.readers.c_sharp import (
    local_declaration_statement as cs_local_declaration_statement,
)
from blends.syntax.readers.c_sharp import (
    member_access_expression as cs_member_access_expression,
)
from blends.syntax.readers.c_sharp import (
    member_binding_expression as cs_member_binding_expression,
)
from blends.syntax.readers.c_sharp import (
    method_declaration as cs_method_declaration,
)
from blends.syntax.readers.c_sharp import (
    name_equals as cs_name_equals,
)
from blends.syntax.readers.c_sharp import (
    namespace_declaration as cs_namespace_declaration,
)
from blends.syntax.readers.c_sharp import (
    null_literal as cs_null_literal,
)
from blends.syntax.readers.c_sharp import (
    number_literal as cs_number_literal,
)
from blends.syntax.readers.c_sharp import (
    object_creation_expression as cs_object_creation_expression,
)
from blends.syntax.readers.c_sharp import (
    parameter as cs_parameter,
)
from blends.syntax.readers.c_sharp import (
    parameter_list as cs_parameter_list,
)
from blends.syntax.readers.c_sharp import (
    parenthesized_expression as cs_parenthesized_expression,
)
from blends.syntax.readers.c_sharp import (
    postfix_unary_expression as cs_postfix_unary_expression,
)
from blends.syntax.readers.c_sharp import (
    prefix_expression as cs_prefix_expression,
)
from blends.syntax.readers.c_sharp import (
    property_declaration as cs_property_declaration,
)
from blends.syntax.readers.c_sharp import (
    return_statement as cs_return_statement,
)
from blends.syntax.readers.c_sharp import (
    string_literal as cs_string_literal,
)
from blends.syntax.readers.c_sharp import (
    switch_body as cs_switch_body,
)
from blends.syntax.readers.c_sharp import (
    switch_section as cs_switch_section,
)
from blends.syntax.readers.c_sharp import (
    switch_statement as cs_switch_statement,
)
from blends.syntax.readers.c_sharp import (
    this_expression as cs_this_expression,
)
from blends.syntax.readers.c_sharp import (
    this_node as cs_this_node,
)
from blends.syntax.readers.c_sharp import (
    throw_statement as cs_throw_statement,
)
from blends.syntax.readers.c_sharp import (
    try_statement as cs_try_statement,
)
from blends.syntax.readers.c_sharp import (
    type_of_expression as cs_type_of_expression,
)
from blends.syntax.readers.c_sharp import (
    type_parameter_list as cs_type_parameter_list,
)
from blends.syntax.readers.c_sharp import (
    unary_expression as cs_unary_expression,
)
from blends.syntax.readers.c_sharp import (
    using_global_directive as cs_using_global_directive,
)
from blends.syntax.readers.c_sharp import (
    using_statement as cs_using_statement,
)
from blends.syntax.readers.c_sharp import (
    variable_declaration as cs_variable_declaration,
)
from blends.syntax.readers.c_sharp import (
    while_statement as cs_while_statement,
)

C_SHARP_DISPATCHERS: Dispatcher = {
    "accessor_declaration": cs_accessor_declaration.reader,
    "anonymous_object_creation_expression": cs_anon_object_creation.reader,
    "argument": cs_argument.reader,
    "attribute_argument": cs_argument.reader,
    "argument_list": cs_argument_list.reader,
    "attribute_argument_list": cs_argument_list.reader,
    "array_creation_expression": cs_array_creation_expression.reader,
    "implicit_array_creation_expression": cs_array_creation_expression.reader,
    "arrow_expression_clause": cs_arrow_expression_clause.reader,
    "assignment_expression": cs_assignment_expression.reader,
    "attribute": cs_attribute.reader,
    "attribute_list": cs_attribute_list.reader,
    "binary_expression": cs_binary_expression.reader,
    "boolean_literal": cs_boolean_literal.reader,
    "bracketed_argument_list": cs_bracketed_argument_list.reader,
    "break_statement": cs_break_statement.reader,
    "block": cs_execution_block.reader,
    "cast_expression": cs_cast_expression.reader,
    "catch_clause": cs_catch_clause.reader,
    "catch_declaration": cs_catch_declaration.reader,
    "class_declaration": cs_class_declaration.reader,
    "comment": cs_comment.reader,
    "compilation_unit": cs_compilation_unit.reader,
    "conditional_access_expression": cs_conditional_access_expression.reader,
    "constructor_declaration": cs_constructor_declaration.reader,
    "continue_statement": cs_continue_statement.reader,
    "declaration_list": cs_declaration_block.reader,
    "do_statement": cs_do_statement.reader,
    "element_access_expression": cs_element_access_expression.reader,
    "element_binding_expression": cs_element_binding_expression.reader,
    "expression_statement": cs_expression_statement.reader,
    "field_declaration": cs_variable_declaration.reader,
    "file_scoped_namespace_declaration": cs_file_scoped_namespace_decla.reader,
    "finally_clause": cs_finally_clause.reader,
    "for_each_statement": cs_for_each_statement.reader,
    "for_statement": cs_for_statement.reader,
    "global_statement": cs_global_statement.reader,
    "identifier": cs_identifier.reader,
    "conditional_expression": cs_if_statement.reader,
    "if_statement": cs_if_statement.reader,
    "initializer_expression": cs_initializer_expression.reader,
    "interface_declaration": cs_interface_declaration.reader,
    "interpolated_string_expression": cs_interpolated_string_expression.reader,
    "invocation_expression": cs_invocation_expression.reader,
    "interpolation": cs_interpolation.reader,
    "interpolation_brace": cs_interpolated_string_expression.reader,
    "lambda_expression": cs_lambda_expression.reader,
    "local_declaration_statement": cs_local_declaration_statement.reader,
    "member_access_expression": cs_member_access_expression.reader,
    "member_binding_expression": cs_member_binding_expression.reader,
    "method_declaration": cs_method_declaration.reader,
    "local_function_statement": cs_method_declaration.reader,
    "name_equals": cs_name_equals.reader,
    "namespace_declaration": cs_namespace_declaration.reader,
    "null_literal": cs_null_literal.reader,
    "integer_literal": cs_number_literal.reader,
    "real_literal": cs_number_literal.reader,
    "object_creation_expression": cs_object_creation_expression.reader,
    "parameter": cs_parameter.reader,
    "implicit_parameter": cs_implicit_parameter.reader,
    "parameter_list": cs_parameter_list.reader,
    "implicit_parameter_list": cs_parameter_list.reader,
    "parenthesized_expression": cs_parenthesized_expression.reader,
    "postfix_unary_expression": cs_postfix_unary_expression.reader,
    "prefix_unary_expression": cs_prefix_expression.reader,
    "property_declaration": cs_property_declaration.reader,
    "return_statement": cs_return_statement.reader,
    "character_literal": cs_string_literal.reader,
    "string_literal": cs_string_literal.reader,
    "verbatim_string_literal": cs_string_literal.reader,
    "predefined_type": cs_string_literal.reader,
    "switch_body": cs_switch_body.reader,
    "switch_statement": cs_switch_statement.reader,
    "switch_section": cs_switch_section.reader,
    "this_expression": cs_this_expression.reader,
    "this": cs_this_node.reader,
    "throw_statement": cs_throw_statement.reader,
    "type_of_expression": cs_type_of_expression.reader,
    "type_parameter_list": cs_type_parameter_list.reader,
    "try_statement": cs_try_statement.reader,
    "using_directive": cs_using_global_directive.reader,
    "using_statement": cs_using_statement.reader,
    "unary_expression": cs_unary_expression.reader,
    "variable_declaration": cs_variable_declaration.reader,
    "while_statement": cs_while_statement.reader,
}
