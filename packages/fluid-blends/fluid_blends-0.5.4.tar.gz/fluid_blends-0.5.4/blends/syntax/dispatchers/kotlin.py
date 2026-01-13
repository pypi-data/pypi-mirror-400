from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.kotlin import (
    annotation as kotlin_annotation,
)
from blends.syntax.readers.kotlin import (
    argument_list as kotlin_argument_list,
)
from blends.syntax.readers.kotlin import (
    assignment_expression as kotlin_assignment_expression,
)
from blends.syntax.readers.kotlin import (
    binary_expression as kotlin_binary_expression,
)
from blends.syntax.readers.kotlin import (
    catch_clause as kotlin_catch_clause,
)
from blends.syntax.readers.kotlin import (
    class_body as kotlin_class_body,
)
from blends.syntax.readers.kotlin import (
    class_declaration as kotlin_class_declaration,
)
from blends.syntax.readers.kotlin import (
    comment as kotlin_comment,
)
from blends.syntax.readers.kotlin import (
    companion_object as kotlin_companion_object,
)
from blends.syntax.readers.kotlin import (
    expression_statement as kotlin_expression_statement,
)
from blends.syntax.readers.kotlin import (
    finally_clause as kotlin_finally_clause,
)
from blends.syntax.readers.kotlin import (
    for_statement as kotlin_for_statement,
)
from blends.syntax.readers.kotlin import (
    identifier as kotlin_identifier,
)
from blends.syntax.readers.kotlin import (
    if_statement as kotlin_if_statement,
)
from blends.syntax.readers.kotlin import (
    import_declaration as kotlin_import_declaration,
)
from blends.syntax.readers.kotlin import (
    index_expression as kotlin_index_expression,
)
from blends.syntax.readers.kotlin import (
    infix_expression as kotlin_infix_expression,
)
from blends.syntax.readers.kotlin import (
    jump_statement as kotlin_jump_statement,
)
from blends.syntax.readers.kotlin import (
    member_access_expression as kotlin_member_access_expression,
)
from blends.syntax.readers.kotlin import (
    method_declaration as kotlin_method_declaration,
)
from blends.syntax.readers.kotlin import (
    method_invocation as kotlin_method_invocation,
)
from blends.syntax.readers.kotlin import (
    modifiers as kotlin_modifiers,
)
from blends.syntax.readers.kotlin import (
    number_literal as kotlin_number_literal,
)
from blends.syntax.readers.kotlin import (
    object as kotlin_object,
)
from blends.syntax.readers.kotlin import (
    parameter as kotlin_parameter,
)
from blends.syntax.readers.kotlin import (
    parameter_list as kotlin_parameter_list,
)
from blends.syntax.readers.kotlin import (
    parenthesized_expression as kotlin_parenthesized_expression,
)
from blends.syntax.readers.kotlin import (
    reserved_word as kotlin_reserved_word,
)
from blends.syntax.readers.kotlin import (
    source_file as kotlin_source_file,
)
from blends.syntax.readers.kotlin import (
    statement_block as kotlin_declaration_block,
)
from blends.syntax.readers.kotlin import (
    statements as kotlin_statements,
)
from blends.syntax.readers.kotlin import (
    string_content as kotlin_string_content,
)
from blends.syntax.readers.kotlin import (
    string_literal as kotlin_string_literal,
)
from blends.syntax.readers.kotlin import (
    try_statement as kotlin_try_statement,
)
from blends.syntax.readers.kotlin import (
    unary_expression as kotlin_unary_expression,
)
from blends.syntax.readers.kotlin import (
    variable_declaration as kotlin_variable_declaration,
)
from blends.syntax.readers.kotlin import (
    when_entry as kotlin_when_entry,
)
from blends.syntax.readers.kotlin import (
    when_expression as kotlin_when_expression,
)
from blends.syntax.readers.kotlin import (
    while_statement as kotlin_while_statement,
)

KOTLIN_DISPATCHERS: Dispatcher = {
    "annotation": kotlin_annotation.reader,
    "anonymous_initializer": kotlin_method_declaration.reader,
    "assignment": kotlin_assignment_expression.reader,
    "binary_expression": kotlin_binary_expression.reader,
    "block": kotlin_declaration_block.reader,
    "call_expression": kotlin_method_invocation.reader,
    "catch_block": kotlin_catch_clause.reader,
    "class_body": kotlin_class_body.reader,
    "class_declaration": kotlin_class_declaration.reader,
    "companion_object": kotlin_companion_object.reader,
    "expression": kotlin_expression_statement.reader,
    "function_body": kotlin_declaration_block.reader,
    "function_value_parameters": kotlin_parameter_list.reader,
    "finally_block": kotlin_finally_clause.reader,
    "for_statement": kotlin_for_statement.reader,
    "function_declaration": kotlin_method_declaration.reader,
    "identifier": kotlin_identifier.reader,
    "in_expression": kotlin_infix_expression.reader,
    "index_expression": kotlin_index_expression.reader,
    "infix_expression": kotlin_infix_expression.reader,
    "if_expression": kotlin_if_statement.reader,
    "import": kotlin_import_declaration.reader,
    "jump_expression": kotlin_jump_statement.reader,
    "lambda_literal": kotlin_declaration_block.reader,
    "block_comment": kotlin_comment.reader,
    "line_comment": kotlin_comment.reader,
    "modifiers": kotlin_modifiers.reader,
    "multiline_comment": kotlin_comment.reader,
    "navigation_expression": kotlin_member_access_expression.reader,
    "null": kotlin_reserved_word.reader,
    "number_literal": kotlin_number_literal.reader,
    "object_declaration": kotlin_class_declaration.reader,
    "object_literal": kotlin_object.reader,
    "package_header": kotlin_import_declaration.reader,
    "parameter": kotlin_parameter.reader,
    "parenthesized_expression": kotlin_parenthesized_expression.reader,
    "property_declaration": kotlin_variable_declaration.reader,
    "range_expression": kotlin_assignment_expression.reader,
    "return_expression": kotlin_jump_statement.reader,
    "source_file": kotlin_source_file.reader,
    "simple_identifier": kotlin_identifier.reader,
    "super_expression": kotlin_reserved_word.reader,
    "statement": kotlin_statements.reader,
    "string_literal": kotlin_string_literal.reader,
    "multiline_string_literal": kotlin_string_literal.reader,
    "string_content": kotlin_string_content.reader,
    "this_expression": kotlin_reserved_word.reader,
    "throw_expression": kotlin_jump_statement.reader,
    "try_expression": kotlin_try_statement.reader,
    "type_identifier": kotlin_identifier.reader,
    "unary_expression": kotlin_unary_expression.reader,
    "value_argument": kotlin_parameter.reader,
    "value_arguments": kotlin_argument_list.reader,
    "when_entry": kotlin_when_entry.reader,
    "when_expression": kotlin_when_expression.reader,
    "while_statement": kotlin_while_statement.reader,
}
