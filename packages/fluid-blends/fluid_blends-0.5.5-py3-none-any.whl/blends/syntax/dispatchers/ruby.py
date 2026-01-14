from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.ruby import (
    argument_list as ruby_argument_list,
)
from blends.syntax.readers.ruby import (
    array_node as ruby_array_node,
)
from blends.syntax.readers.ruby import (
    assignment as ruby_assignment,
)
from blends.syntax.readers.ruby import (
    begin as ruby_begin,
)
from blends.syntax.readers.ruby import (
    binary_expression as ruby_binary_expression,
)
from blends.syntax.readers.ruby import (
    boolean_literal as ruby_boolean_literal,
)
from blends.syntax.readers.ruby import (
    call as ruby_call,
)
from blends.syntax.readers.ruby import (
    catch_declaration as ruby_catch_declaration,
)
from blends.syntax.readers.ruby import (
    class_definition as ruby_class_definition,
)
from blends.syntax.readers.ruby import (
    comment as ruby_comment,
)
from blends.syntax.readers.ruby import (
    element_reference as ruby_element_reference,
)
from blends.syntax.readers.ruby import (
    exception_variable as ruby_exception_variable,
)
from blends.syntax.readers.ruby import (
    execution_block as ruby_execution_block,
)
from blends.syntax.readers.ruby import (
    for_statement as ruby_for_statement,
)
from blends.syntax.readers.ruby import (
    hash as ruby_hash,
)
from blends.syntax.readers.ruby import (
    identifier as ruby_identifier,
)
from blends.syntax.readers.ruby import (
    if_conditional as ruby_if_conditional,
)
from blends.syntax.readers.ruby import (
    if_modifier as ruby_if_modifier,
)
from blends.syntax.readers.ruby import (
    integer as ruby_integer,
)
from blends.syntax.readers.ruby import (
    method_declaration as ruby_method_declaration,
)
from blends.syntax.readers.ruby import (
    method_parameters as ruby_method_parameters,
)
from blends.syntax.readers.ruby import (
    module_definition as ruby_module_definition,
)
from blends.syntax.readers.ruby import (
    pair as ruby_pair,
)
from blends.syntax.readers.ruby import (
    parameter as ruby_parameter,
)
from blends.syntax.readers.ruby import (
    parameters as ruby_parameters,
)
from blends.syntax.readers.ruby import (
    program as ruby_program,
)
from blends.syntax.readers.ruby import (
    return_statement as ruby_return_statement,
)
from blends.syntax.readers.ruby import (
    scope_resolution as ruby_scope_resolution,
)
from blends.syntax.readers.ruby import (
    string_content as ruby_string_content,
)
from blends.syntax.readers.ruby import (
    string_literal as ruby_string_literal,
)
from blends.syntax.readers.ruby import (
    subshell as ruby_subshell,
)
from blends.syntax.readers.ruby import (
    try_statement as ruby_try_statement,
)
from blends.syntax.readers.ruby import (
    unless as ruby_unless,
)
from blends.syntax.readers.ruby import (
    while_statement as ruby_while_statement,
)

RUBY_DISPATCHERS: Dispatcher = {
    "array": ruby_array_node.reader,
    "argument_list": ruby_argument_list.reader,
    "assignment": ruby_assignment.reader,
    "exception_variable": ruby_exception_variable.reader,
    "binary": ruby_binary_expression.reader,
    "block_parameter": ruby_parameter.reader,
    "block_parameters": ruby_parameters.reader,
    "body_statement": ruby_execution_block.reader,
    "call": ruby_call.reader,
    "rescue": ruby_catch_declaration.reader,
    "class": ruby_class_definition.reader,
    "comment": ruby_comment.reader,
    "constant": ruby_identifier.reader,
    "do": ruby_execution_block.reader,
    "do_block": ruby_execution_block.reader,
    "else": ruby_execution_block.reader,
    "elsif": ruby_if_conditional.reader,
    "false": ruby_boolean_literal.reader,
    "for": ruby_for_statement.reader,
    "hash": ruby_hash.reader,
    "hash_key_symbol": ruby_identifier.reader,
    "hash_splat_parameter": ruby_parameter.reader,
    "identifier": ruby_identifier.reader,
    "if_modifier": ruby_if_modifier.reader,
    "if": ruby_if_conditional.reader,
    "instance_variable": ruby_identifier.reader,
    "integer": ruby_integer.reader,
    "method": ruby_method_declaration.reader,
    "method_parameters": ruby_method_parameters.reader,
    "module": ruby_module_definition.reader,
    "optional_parameter": ruby_parameter.reader,
    "pair": ruby_pair.reader,
    "program": ruby_program.reader,
    "regex": ruby_string_literal.reader,
    "return": ruby_return_statement.reader,
    "scope_resolution": ruby_scope_resolution.reader,
    "simple_symbol": ruby_identifier.reader,
    "singleton_class": ruby_class_definition.reader,
    "singleton_method": ruby_method_declaration.reader,
    "splat_parameter": ruby_parameter.reader,
    "string": ruby_string_literal.reader,
    "string_content": ruby_string_content.reader,
    "subshell": ruby_subshell.reader,
    "then": ruby_execution_block.reader,
    "true": ruby_boolean_literal.reader,
    "while": ruby_while_statement.reader,
    "while_modifier": ruby_while_statement.reader,
    "block": ruby_execution_block.reader,
    "block_body": ruby_execution_block.reader,
    "rescue_modifier": ruby_try_statement.reader,
    "begin": ruby_begin.reader,
    "element_reference": ruby_element_reference.reader,
    "unless": ruby_unless.reader,
}
