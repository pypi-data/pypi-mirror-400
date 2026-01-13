from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.scala import (
    annotation as scala_annotation,
)
from blends.syntax.readers.scala import (
    argument_list as scala_argument_list,
)
from blends.syntax.readers.scala import (
    array_node as scala_array_node,
)
from blends.syntax.readers.scala import (
    assignment as scala_assignment,
)
from blends.syntax.readers.scala import (
    binary_expression as scala_binary_expression,
)
from blends.syntax.readers.scala import (
    boolean_literal as scala_boolean_literal,
)
from blends.syntax.readers.scala import (
    call_expression as scala_call_expression,
)
from blends.syntax.readers.scala import (
    class_definition as scala_class_definition,
)
from blends.syntax.readers.scala import (
    comment as scala_comment,
)
from blends.syntax.readers.scala import (
    conditional_expression as scala_conditional_expression,
)
from blends.syntax.readers.scala import (
    do_statement as scala_do_statement,
)
from blends.syntax.readers.scala import (
    except_clause as scala_except_clause,
)
from blends.syntax.readers.scala import (
    execution_block as scala_execution_block,
)
from blends.syntax.readers.scala import (
    field_expression as scala_field_expression,
)
from blends.syntax.readers.scala import (
    finally_clause as scala_finally_clause,
)
from blends.syntax.readers.scala import (
    for_statement as scala_for_statement,
)
from blends.syntax.readers.scala import (
    identifier as scala_identifier,
)
from blends.syntax.readers.scala import (
    import_global as scala_import_global,
)
from blends.syntax.readers.scala import (
    interface_declaration as scala_interface_declaration,
)
from blends.syntax.readers.scala import (
    lambda_expression as scala_lambda_expression,
)
from blends.syntax.readers.scala import (
    method_declaration as scala_method_declaration,
)
from blends.syntax.readers.scala import (
    number_literal as scala_number_literal,
)
from blends.syntax.readers.scala import (
    object_creation_expression as scala_object_creation_expression,
)
from blends.syntax.readers.scala import (
    package_declaration as scala_package_declaration,
)
from blends.syntax.readers.scala import (
    parameter as scala_parameter,
)
from blends.syntax.readers.scala import (
    parameter_list as scala_parameter_list,
)
from blends.syntax.readers.scala import (
    parenthesized_expression as scala_parenthesized_expression,
)
from blends.syntax.readers.scala import (
    program as scala_program,
)
from blends.syntax.readers.scala import (
    property_declaration as scala_property_declaration,
)
from blends.syntax.readers.scala import (
    return_statement as scala_return_statement,
)
from blends.syntax.readers.scala import (
    string_literal as scala_string_literal,
)
from blends.syntax.readers.scala import (
    switch_section as scala_switch_section,
)
from blends.syntax.readers.scala import (
    switch_statement as scala_switch_statement,
)
from blends.syntax.readers.scala import (
    throw_statement as scala_throw_statement,
)
from blends.syntax.readers.scala import (
    try_statement as scala_try_statement,
)
from blends.syntax.readers.scala import (
    variable_declaration as scala_variable_declaration,
)
from blends.syntax.readers.scala import (
    while_statement as scala_while_statement,
)

SCALA_DISPATCHERS: Dispatcher = {
    "annotation": scala_annotation.reader,
    "ascription_expression": scala_parameter.reader,
    "finally_clause": scala_finally_clause.reader,
    "parameters": scala_argument_list.reader,
    "arguments": scala_argument_list.reader,
    "function_definition": scala_method_declaration.reader,
    "function_declaration": scala_method_declaration.reader,
    "comment": scala_comment.reader,
    "block_comment": scala_comment.reader,
    "template_body": scala_execution_block.reader,
    "block": scala_execution_block.reader,
    "case_block": scala_execution_block.reader,
    "call_expression": scala_call_expression.reader,
    "class_definition": scala_class_definition.reader,
    "if_expression": scala_conditional_expression.reader,
    "val_definition": scala_variable_declaration.reader,
    "var_definition": scala_variable_declaration.reader,
    "boolean_literal": scala_boolean_literal.reader,
    "integer_literal": scala_number_literal.reader,
    "floating_point_literal": scala_number_literal.reader,
    "for_expression": scala_for_statement.reader,
    "character_literal": scala_string_literal.reader,
    "string": scala_string_literal.reader,
    "interpolated_string_expression": scala_string_literal.reader,
    "identifier": scala_identifier.reader,
    "type_identifier": scala_identifier.reader,
    "object_definition": scala_class_definition.reader,
    "compilation_unit": scala_program.reader,
    "assignment_expression": scala_assignment.reader,
    "while_expression": scala_while_statement.reader,
    "infix_expression": scala_binary_expression.reader,
    "parenthesized_expression": scala_parenthesized_expression.reader,
    "do_while_expression": scala_do_statement.reader,
    "match_expression": scala_switch_statement.reader,
    "parameter": scala_parameter.reader,
    "class_parameter": scala_parameter.reader,
    "catch_clause": scala_except_clause.reader,
    "case_clause": scala_switch_section.reader,
    "try_expression": scala_try_statement.reader,
    "return_expression": scala_return_statement.reader,
    "import_declaration": scala_import_global.reader,
    "lambda_expression": scala_lambda_expression.reader,
    "binding": scala_parameter_list.reader,
    "class_parameters": scala_parameter_list.reader,
    "trait_definition": scala_interface_declaration.reader,
    "field_expression": scala_field_expression.reader,
    "instance_expression": scala_object_creation_expression.reader,
    "generic_function": scala_call_expression.reader,
    "throw_expression": scala_throw_statement.reader,
    "type_parameters": scala_argument_list.reader,
    "tuple_expression": scala_array_node.reader,
    "package_clause": scala_package_declaration.reader,
    "type_definition": scala_property_declaration.reader,
    "indented_block": scala_execution_block.reader,
    "wildcard": scala_identifier.reader,
}
