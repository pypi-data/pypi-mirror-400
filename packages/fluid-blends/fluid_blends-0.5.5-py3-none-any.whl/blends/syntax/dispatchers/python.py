from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.python import (
    argument as python_argument,
)
from blends.syntax.readers.python import (
    argument_list as python_argument_list,
)
from blends.syntax.readers.python import (
    array_node as python_array,
)
from blends.syntax.readers.python import (
    as_pattern as python_as_pattern,
)
from blends.syntax.readers.python import (
    assert_statement as python_assert_statement,
)
from blends.syntax.readers.python import (
    assignment as python_assignment,
)
from blends.syntax.readers.python import (
    attribute as python_attribute,
)
from blends.syntax.readers.python import (
    await_expression as python_await_expression,
)
from blends.syntax.readers.python import (
    binary_expression as python_binary_expression,
)
from blends.syntax.readers.python import (
    boolean_literal as python_boolean_literal,
)
from blends.syntax.readers.python import (
    break_statement as python_break_statement,
)
from blends.syntax.readers.python import (
    call as python_call,
)
from blends.syntax.readers.python import (
    class_definition as python_class_definition,
)
from blends.syntax.readers.python import (
    comment as python_comment,
)
from blends.syntax.readers.python import (
    comprehension as python_comprehension,
)
from blends.syntax.readers.python import (
    conditional_expression as python_conditional_expression,
)
from blends.syntax.readers.python import (
    continue_statement as python_continue_statement,
)
from blends.syntax.readers.python import (
    decorated_definition as python_decorated_definition,
)
from blends.syntax.readers.python import (
    decorator as python_decorator,
)
from blends.syntax.readers.python import (
    dictionary as python_dictionary,
)
from blends.syntax.readers.python import (
    dictionary_splat as python_dictionary_splat,
)
from blends.syntax.readers.python import (
    else_clause as python_else_clause,
)
from blends.syntax.readers.python import (
    except_clause as python_except_clause,
)
from blends.syntax.readers.python import (
    execution_block as python_execution_block,
)
from blends.syntax.readers.python import (
    expression_statement as python_expression_statement,
)
from blends.syntax.readers.python import (
    finally_clause as python_finally_clause,
)
from blends.syntax.readers.python import (
    for_in_clause as python_for_in_clause,
)
from blends.syntax.readers.python import (
    for_statement as python_for_statement,
)
from blends.syntax.readers.python import (
    function_definition as python_function_definition,
)
from blends.syntax.readers.python import (
    generator_expression as python_generator_expression,
)
from blends.syntax.readers.python import (
    identifier as python_identifier,
)
from blends.syntax.readers.python import (
    if_clause as python_if_clause,
)
from blends.syntax.readers.python import (
    if_statement as python_if_statement,
)
from blends.syntax.readers.python import (
    import_global as python_import_global,
)
from blends.syntax.readers.python import (
    module as python_module,
)
from blends.syntax.readers.python import (
    named_expression as python_named_expression,
)
from blends.syntax.readers.python import (
    not_operator as python_not_operator,
)
from blends.syntax.readers.python import (
    number_literal as python_number_literal,
)
from blends.syntax.readers.python import (
    pair as python_pair,
)
from blends.syntax.readers.python import (
    parameter as python_parameter,
)
from blends.syntax.readers.python import (
    parameters as python_parameters,
)
from blends.syntax.readers.python import (
    parenthesized_expression as python_parenthesized_expression,
)
from blends.syntax.readers.python import (
    raise_statement as python_raise_statement,
)
from blends.syntax.readers.python import (
    reserved_word as python_reserved_word,
)
from blends.syntax.readers.python import (
    return_statement as python_return_statement,
)
from blends.syntax.readers.python import (
    splat_pattern as python_splat_pattern,
)
from blends.syntax.readers.python import (
    string_literal as python_string_literal,
)
from blends.syntax.readers.python import (
    subscript as python_subscript,
)
from blends.syntax.readers.python import (
    try_statement as python_try_statement,
)
from blends.syntax.readers.python import (
    using_statement as python_using_statement,
)
from blends.syntax.readers.python import (
    while_statement as python_while_statement,
)

PYTHON_DISPATCHERS: Dispatcher = {
    "argument_list": python_argument_list.reader,
    "keyword_argument": python_argument.reader,
    "list": python_array.reader,
    "tuple": python_array.reader,
    "tuple_pattern": python_array.reader,
    "pattern_list": python_array.reader,
    "set": python_array.reader,
    "as_pattern": python_as_pattern.reader,
    "assert_statement": python_assert_statement.reader,
    "assignment": python_assignment.reader,
    "attribute": python_attribute.reader,
    "await": python_await_expression.reader,
    "augmented_assignment": python_binary_expression.reader,
    "binary_operator": python_binary_expression.reader,
    "boolean_operator": python_binary_expression.reader,
    "comparison_operator": python_binary_expression.reader,
    "false": python_boolean_literal.reader,
    "true": python_boolean_literal.reader,
    "break_statement": python_break_statement.reader,
    "call": python_call.reader,
    "class_definition": python_class_definition.reader,
    "comment": python_comment.reader,
    "continue_statement": python_continue_statement.reader,
    "pass_statement": python_continue_statement.reader,
    "conditional_expression": python_conditional_expression.reader,
    "decorated_definition": python_decorated_definition.reader,
    "decorator": python_decorator.reader,
    "dictionary": python_dictionary.reader,
    "dictionary_splat": python_dictionary_splat.reader,
    "else_clause": python_else_clause.reader,
    "except_clause": python_except_clause.reader,
    "block": python_execution_block.reader,
    "delete_statement": python_expression_statement.reader,
    "expression_statement": python_expression_statement.reader,
    "global_statement": python_expression_statement.reader,
    "finally_clause": python_finally_clause.reader,
    "for_in_clause": python_for_in_clause.reader,
    "for_statement": python_for_statement.reader,
    "function_definition": python_function_definition.reader,
    "generator_expression": python_generator_expression.reader,
    "identifier": python_identifier.reader,
    "if_clause": python_if_clause.reader,
    "elif_clause": python_if_statement.reader,
    "if_statement": python_if_statement.reader,
    "dotted_name": python_import_global.reader,
    "dictionary_comprehension": python_comprehension.reader,
    "list_comprehension": python_comprehension.reader,
    "set_comprehension": python_comprehension.reader,
    "module": python_module.reader,
    "named_expression": python_named_expression.reader,
    "not_operator": python_not_operator.reader,
    "integer": python_number_literal.reader,
    "float": python_number_literal.reader,
    "pair": python_pair.reader,
    "default_parameter": python_parameter.reader,
    "parameter": python_parameter.reader,
    "typed_parameter": python_parameter.reader,
    "typed_default_parameter": python_parameter.reader,
    "parameters": python_parameters.reader,
    "parenthesized_expression": python_parenthesized_expression.reader,
    "raise_statement": python_raise_statement.reader,
    "in": python_reserved_word.reader,
    "none": python_reserved_word.reader,
    "pass": python_reserved_word.reader,
    "return": python_reserved_word.reader,
    "return_statement": python_return_statement.reader,
    "yield": python_return_statement.reader,
    "list_splat_pattern": python_splat_pattern.reader,
    "dictionary_splat_pattern": python_splat_pattern.reader,
    "expression_list": python_string_literal.reader,
    "list_splat": python_string_literal.reader,
    "slice": python_string_literal.reader,
    "string": python_string_literal.reader,
    "subscript": python_subscript.reader,
    "try_statement": python_try_statement.reader,
    "with_statement": python_using_statement.reader,
    "while_statement": python_while_statement.reader,
}
