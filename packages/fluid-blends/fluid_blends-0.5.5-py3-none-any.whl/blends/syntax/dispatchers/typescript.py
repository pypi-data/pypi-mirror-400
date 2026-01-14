from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.javascript import (
    arguments as javascript_arguments,
)
from blends.syntax.readers.javascript import (
    array_node as javascript_array,
)
from blends.syntax.readers.javascript import (
    assignment_expression as javascript_assignment_expression,
)
from blends.syntax.readers.javascript import (
    await_expression as javascript_await_expression,
)
from blends.syntax.readers.javascript import (
    binary_expression as javascript_binary_expression,
)
from blends.syntax.readers.javascript import (
    boolean_literal as javascript_boolean_literal,
)
from blends.syntax.readers.javascript import (
    break_statement as javascript_break_statement,
)
from blends.syntax.readers.javascript import (
    call_expression as javascript_call_expression,
)
from blends.syntax.readers.javascript import (
    catch_clause as javascript_catch_clause,
)
from blends.syntax.readers.javascript import (
    class_declaration as javascript_class_declaration,
)
from blends.syntax.readers.javascript import (
    comment as javascript_comment,
)
from blends.syntax.readers.javascript import (
    debugger_statement as javascript_debugger_statement,
)
from blends.syntax.readers.javascript import (
    do_statement as javascript_do_statement,
)
from blends.syntax.readers.javascript import (
    else_clause as javascript_else_clause,
)
from blends.syntax.readers.javascript import (
    execution_block as javascript_execution_block,
)
from blends.syntax.readers.javascript import (
    export_statement as javascript_export_statement,
)
from blends.syntax.readers.javascript import (
    expression_statement as javascript_expression_statement,
)
from blends.syntax.readers.javascript import (
    finally_clause as javascript_finally_clause,
)
from blends.syntax.readers.javascript import (
    for_each_statement as javascript_for_each_statement,
)
from blends.syntax.readers.javascript import (
    for_statement as javascript_for_statement,
)
from blends.syntax.readers.javascript import (
    identifier as javascript_identifier,
)
from blends.syntax.readers.javascript import (
    if_statement as javascript_if_statement,
)
from blends.syntax.readers.javascript import (
    import_global as javascript_import_global,
)
from blends.syntax.readers.javascript import (
    import_module as javascript_import_module,
)
from blends.syntax.readers.javascript import (
    jsx_attribute as javascript_jsx_attribute,
)
from blends.syntax.readers.javascript import (
    jsx_element as javascript_jsx_element,
)
from blends.syntax.readers.javascript import (
    jsx_self_closing_element as javascript_jsx_self_closing_element,
)
from blends.syntax.readers.javascript import (
    member_expression as javascript_member_expression,
)
from blends.syntax.readers.javascript import (
    method_declaration as javascript_method_declaration,
)
from blends.syntax.readers.javascript import (
    nested_identifier as javascript_nested_identifier,
)
from blends.syntax.readers.javascript import (
    new_expression as javascript_new_expression,
)
from blends.syntax.readers.javascript import (
    number_literal as javascript_number_literal,
)
from blends.syntax.readers.javascript import (
    object as javascript_object,
)
from blends.syntax.readers.javascript import (
    pair as javascript_pair,
)
from blends.syntax.readers.javascript import (
    parameter_list as javascript_parameter_list,
)
from blends.syntax.readers.javascript import (
    parenthesized_expression as javascript_parenthesized_expression,
)
from blends.syntax.readers.javascript import (
    program as javascript_program,
)
from blends.syntax.readers.javascript import (
    rest_pattern as typescript_rest_pattern,
)
from blends.syntax.readers.javascript import (
    return_statement as javascript_return_statement,
)
from blends.syntax.readers.javascript import (
    spread_element as typescript_spread_element,
)
from blends.syntax.readers.javascript import (
    string_literal as javascript_string_literal,
)
from blends.syntax.readers.javascript import (
    subscript_expression as javascript_subscript_expression,
)
from blends.syntax.readers.javascript import (
    switch_body as javascript_switch_body,
)
from blends.syntax.readers.javascript import (
    switch_section as javascript_switch_section,
)
from blends.syntax.readers.javascript import (
    switch_statement as javascript_switch_statement,
)
from blends.syntax.readers.javascript import (
    template_string as javascript_template_string,
)
from blends.syntax.readers.javascript import (
    this_node as javascript_this,
)
from blends.syntax.readers.javascript import (
    throw_statement as javascript_throw_statement,
)
from blends.syntax.readers.javascript import (
    try_statement as javascript_try_statement,
)
from blends.syntax.readers.javascript import (
    unary_expression as javascript_unary_expression,
)
from blends.syntax.readers.javascript import (
    update_expression as javascript_update_expression,
)
from blends.syntax.readers.javascript import (
    variable_declaration as javascript_variable_declaration,
)
from blends.syntax.readers.javascript import (
    while_statement as javascript_while_statement,
)
from blends.syntax.readers.javascript import (
    yield_expression as javascript_yield_expression,
)
from blends.syntax.readers.typescript import (
    ambient_declaration as typescript_ambient_declaration,
)
from blends.syntax.readers.typescript import (
    arrow_function as javascript_arrow_function,
)
from blends.syntax.readers.typescript import (
    as_expression as typescript_as_expression,
)
from blends.syntax.readers.typescript import (
    class_body as typescript_class_body,
)
from blends.syntax.readers.typescript import (
    empty_statement as typescript_empty_statement,
)
from blends.syntax.readers.typescript import (
    enum_assignment as typescript_enum_assignment,
)
from blends.syntax.readers.typescript import (
    enum_body as typescript_enum_body,
)
from blends.syntax.readers.typescript import (
    enum_declaration as typescript_enum_declaration,
)
from blends.syntax.readers.typescript import (
    function_signature as typescript_function_signature,
)
from blends.syntax.readers.typescript import (
    function_type as typescript_function_type,
)
from blends.syntax.readers.typescript import (
    generic_type as typescript_generic_type,
)
from blends.syntax.readers.typescript import (
    index_signature as typescript_index_signature,
)
from blends.syntax.readers.typescript import (
    interface_declaration as typescript_interface_declaration,
)
from blends.syntax.readers.typescript import (
    internal_module as typescript_internal_module,
)
from blends.syntax.readers.typescript import (
    intersection_type as typescript_intersection_type,
)
from blends.syntax.readers.typescript import (
    parenthesized_type as typescript_parenthesized_type,
)
from blends.syntax.readers.typescript import (
    predefined_type as typescript_predefined_type,
)
from blends.syntax.readers.typescript import (
    property_signature as typescript_property_signature,
)
from blends.syntax.readers.typescript import (
    public_field_definition as typescript_public_field_definition,
)
from blends.syntax.readers.typescript import (
    required_parameter as typescript_required_parameter,
)
from blends.syntax.readers.typescript import (
    ternary_expression as typescript_ternary_expression,
)
from blends.syntax.readers.typescript import (
    tuple_type as typescript_tuple_type,
)
from blends.syntax.readers.typescript import (
    type_alias_declaration as typescript_type_alias_declaration,
)
from blends.syntax.readers.typescript import (
    type_annotation as typescript_type_annotation,
)
from blends.syntax.readers.typescript import (
    union_type as typescript_union_type,
)
from blends.syntax.readers.typescript import (
    void as typescript_void,
)

TYPESCRIPT_DISPATCHERS: Dispatcher = {
    "ambient_declaration": typescript_ambient_declaration.reader,
    "arguments": javascript_arguments.reader,
    "array": javascript_array.reader,
    "arrow_function": javascript_arrow_function.reader,
    "as_expression": typescript_as_expression.reader,
    "assignment_expression": javascript_assignment_expression.reader,
    "augmented_assignment_expression": javascript_assignment_expression.reader,
    "await_expression": javascript_await_expression.reader,
    "binary_expression": javascript_binary_expression.reader,
    "break_statement": javascript_break_statement.reader,
    "call_expression": javascript_call_expression.reader,
    "class_body": typescript_class_body.reader,
    "catch_clause": javascript_catch_clause.reader,
    "class_declaration": javascript_class_declaration.reader,
    "comment": javascript_comment.reader,
    "debugger_statement": javascript_debugger_statement.reader,
    "do_statement": javascript_do_statement.reader,
    "enum_assignment": typescript_enum_assignment.reader,
    "enum_body": typescript_enum_body.reader,
    "enum_declaration": typescript_enum_declaration.reader,
    "empty_statement": typescript_empty_statement.reader,
    "else_clause": javascript_else_clause.reader,
    "export_statement": javascript_export_statement.reader,
    "expression_statement": javascript_expression_statement.reader,
    "finally_clause": javascript_finally_clause.reader,
    "for_in_statement": javascript_for_each_statement.reader,
    "for_statement": javascript_for_statement.reader,
    "formal_parameters": javascript_parameter_list.reader,
    "type_arguments": javascript_parameter_list.reader,
    "boolean": javascript_boolean_literal.reader,
    "false": javascript_boolean_literal.reader,
    "true": javascript_boolean_literal.reader,
    "function_signature": typescript_function_signature.reader,
    "function_type": typescript_function_type.reader,
    "generic_type": typescript_generic_type.reader,
    "identifier": javascript_identifier.reader,
    "property_identifier": javascript_identifier.reader,
    "shorthand_property_identifier": javascript_identifier.reader,
    "shorthand_property_identifier_pattern": javascript_identifier.reader,
    "type_identifier": javascript_identifier.reader,
    "if_statement": javascript_if_statement.reader,
    "import_statement": javascript_import_global.reader,
    "import_specifier": javascript_import_module.reader,
    "index_signature": typescript_index_signature.reader,
    "interface_declaration": typescript_interface_declaration.reader,
    "internal_module": typescript_internal_module.reader,
    "intersection_type": typescript_intersection_type.reader,
    "member_expression": javascript_member_expression.reader,
    "function": javascript_method_declaration.reader,
    "function_declaration": javascript_method_declaration.reader,
    "generator_function_declaration": javascript_method_declaration.reader,
    "method_definition": javascript_method_declaration.reader,
    "function_expression": javascript_method_declaration.reader,
    "new_expression": javascript_new_expression.reader,
    "number": javascript_number_literal.reader,
    "nested_identifier": javascript_nested_identifier.reader,
    "object": javascript_object.reader,
    "object_type": javascript_object.reader,
    "interface_body": javascript_object.reader,
    "pair": javascript_pair.reader,
    "parenthesized_type": typescript_parenthesized_type.reader,
    "parenthesized_expression": javascript_parenthesized_expression.reader,
    "program": javascript_program.reader,
    "optional_type": typescript_predefined_type.reader,
    "array_type": typescript_predefined_type.reader,
    "literal_type": typescript_predefined_type.reader,
    "predefined_type": typescript_predefined_type.reader,
    "property_signature": typescript_property_signature.reader,
    "public_field_definition": typescript_public_field_definition.reader,
    "optional_parameter": typescript_required_parameter.reader,
    "required_parameter": typescript_required_parameter.reader,
    "rest_pattern": typescript_rest_pattern.reader,
    "return_statement": javascript_return_statement.reader,
    "statement_block": javascript_execution_block.reader,
    "regex": javascript_string_literal.reader,
    "string": javascript_string_literal.reader,
    "subscript_expression": javascript_subscript_expression.reader,
    "switch_body": javascript_switch_body.reader,
    "switch_case": javascript_switch_section.reader,
    "switch_default": javascript_switch_section.reader,
    "switch_statement": javascript_switch_statement.reader,
    "template_string": javascript_template_string.reader,
    "super": javascript_this.reader,
    "this": javascript_this.reader,
    "ternary_expression": typescript_ternary_expression.reader,
    "throw_statement": javascript_throw_statement.reader,
    "try_statement": javascript_try_statement.reader,
    "jsx_element": javascript_jsx_element.reader,
    "jsx_fragment": javascript_jsx_element.reader,
    "jsx_self_closing_element": javascript_jsx_self_closing_element.reader,
    "jsx_opening_element": javascript_jsx_element.reader,
    "jsx_attribute": javascript_jsx_attribute.reader,
    "spread_element": typescript_spread_element.reader,
    "tuple_type": typescript_tuple_type.reader,
    "type_annotation": typescript_type_annotation.reader,
    "type_alias_declaration": typescript_type_alias_declaration.reader,
    "unary_expression": javascript_unary_expression.reader,
    "union_type": typescript_union_type.reader,
    "update_expression": javascript_update_expression.reader,
    "lexical_declaration": javascript_variable_declaration.reader,
    "variable_declaration": javascript_variable_declaration.reader,
    "any": typescript_void.reader,
    "null": typescript_void.reader,
    "undefined": typescript_void.reader,
    "unknown": typescript_void.reader,
    "void": typescript_void.reader,
    "while_statement": javascript_while_statement.reader,
    "yield_expression": javascript_yield_expression.reader,
}
