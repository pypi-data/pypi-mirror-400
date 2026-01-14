from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.go import (
    argument_list as go_argument_list,
)
from blends.syntax.readers.go import (
    assignment_statement as go_assignment_statement,
)
from blends.syntax.readers.go import (
    binary_expression as go_binary_expression,
)
from blends.syntax.readers.go import (
    block as go_block,
)
from blends.syntax.readers.go import (
    boolean_literal as go_boolean_literal,
)
from blends.syntax.readers.go import (
    break_statement as go_break_statement,
)
from blends.syntax.readers.go import (
    call_expression as go_call_expression,
)
from blends.syntax.readers.go import (
    comment as go_comment,
)
from blends.syntax.readers.go import (
    composite_literal as go_composite_literal,
)
from blends.syntax.readers.go import (
    expression_list as go_expression_list,
)
from blends.syntax.readers.go import (
    expression_statement as go_expression_statement,
)
from blends.syntax.readers.go import (
    for_statement as go_for_statement,
)
from blends.syntax.readers.go import (
    function_declaration as go_function_declaration,
)
from blends.syntax.readers.go import (
    identifier as go_identifier,
)
from blends.syntax.readers.go import (
    if_statement as go_if_statement,
)
from blends.syntax.readers.go import (
    import_declaration as go_import_declaration,
)
from blends.syntax.readers.go import (
    index_expression as go_index_expression,
)
from blends.syntax.readers.go import (
    int_literal as go_int_literal,
)
from blends.syntax.readers.go import (
    literal_value as go_literal_value,
)
from blends.syntax.readers.go import (
    nil as go_nil,
)
from blends.syntax.readers.go import (
    package_clause as go_package_clause,
)
from blends.syntax.readers.go import (
    pair as go_pair,
)
from blends.syntax.readers.go import (
    parameter_declaration as go_parameter_declaration,
)
from blends.syntax.readers.go import (
    parameter_list as go_parameter_list,
)
from blends.syntax.readers.go import (
    qualified_type as go_qualified_type,
)
from blends.syntax.readers.go import (
    reserved_words as go_reserved_words,
)
from blends.syntax.readers.go import (
    return_statement as go_return_statement,
)
from blends.syntax.readers.go import (
    selector_expression as go_selector_expression,
)
from blends.syntax.readers.go import (
    slice_expression as go_slice_expression,
)
from blends.syntax.readers.go import (
    source_file as go_source_file,
)
from blends.syntax.readers.go import (
    spread_element as go_spread_element,
)
from blends.syntax.readers.go import (
    string_literal as go_string_literal,
)
from blends.syntax.readers.go import (
    switch_section as go_switch_section,
)
from blends.syntax.readers.go import (
    switch_statement as go_switch_statement,
)
from blends.syntax.readers.go import (
    type_conversion as go_type_conversion,
)
from blends.syntax.readers.go import (
    type_declaration as go_type_declaration,
)
from blends.syntax.readers.go import (
    unary_expression as go_unary_expression,
)
from blends.syntax.readers.go import (
    var_declaration as go_var_declaration,
)

GO_DISPATCHERS: Dispatcher = {
    "argument_list": go_argument_list.reader,
    "assignment_statement": go_assignment_statement.reader,
    "short_var_declaration": go_assignment_statement.reader,
    "block": go_block.reader,
    "binary_expression": go_binary_expression.reader,
    "break_statement": go_break_statement.reader,
    "false": go_boolean_literal.reader,
    "true": go_boolean_literal.reader,
    "call_expression": go_call_expression.reader,
    "comment": go_comment.reader,
    "composite_literal": go_composite_literal.reader,
    "expression_list": go_expression_list.reader,
    "expression_case": go_switch_section.reader,
    "default_case": go_switch_section.reader,
    "expression_statement": go_expression_statement.reader,
    "for_statement": go_for_statement.reader,
    "func_literal": go_function_declaration.reader,
    "function_declaration": go_function_declaration.reader,
    "method_declaration": go_function_declaration.reader,
    "blank_identifier": go_identifier.reader,
    "identifier": go_identifier.reader,
    "field_identifier": go_identifier.reader,
    "package_identifier": go_identifier.reader,
    "type_identifier": go_identifier.reader,
    "literal_value": go_literal_value.reader,
    "if_statement": go_if_statement.reader,
    "import_spec": go_import_declaration.reader,
    "index_expression": go_index_expression.reader,
    "int_literal": go_int_literal.reader,
    "nil": go_nil.reader,
    "package_clause": go_package_clause.reader,
    "parameter_declaration": go_parameter_declaration.reader,
    "parameter_list": go_parameter_list.reader,
    "qualified_type": go_qualified_type.reader,
    "defer_statement": go_reserved_words.reader,
    "return_statement": go_return_statement.reader,
    "selector_expression": go_selector_expression.reader,
    "slice_expression": go_slice_expression.reader,
    "source_file": go_source_file.reader,
    "interpreted_string_literal": go_string_literal.reader,
    "raw_string_literal": go_string_literal.reader,
    "type_case": go_switch_section.reader,
    "type_declaration": go_type_declaration.reader,
    "expression_switch_statement": go_switch_statement.reader,
    "type_assertion_expression": go_unary_expression.reader,
    "type_switch_statement": go_switch_statement.reader,
    "type_conversion_expression": go_type_conversion.reader,
    "unary_expression": go_unary_expression.reader,
    "const_declaration": go_var_declaration.reader,
    "var_declaration": go_var_declaration.reader,
    "variadic_argument": go_spread_element.reader,
    "keyed_element": go_pair.reader,
}
