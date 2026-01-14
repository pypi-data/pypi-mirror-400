from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.hcl import (
    attribute as hcl_attribute,
)
from blends.syntax.readers.hcl import (
    block as hcl_block,
)
from blends.syntax.readers.hcl import (
    config_file as hcl_config_file,
)
from blends.syntax.readers.hcl import (
    expression as hcl_expression,
)
from blends.syntax.readers.hcl import (
    function_arguments as hcl_function_arguments,
)
from blends.syntax.readers.hcl import (
    identifier as hcl_identifier,
)

HCL_DISPATCHERS: Dispatcher = {
    "attribute": hcl_attribute.reader,
    "object_elem": hcl_attribute.reader,
    "block": hcl_block.reader,
    "config_file": hcl_config_file.reader,
    "expression": hcl_expression.reader,
    "function_arguments": hcl_function_arguments.reader,
    "identifier": hcl_identifier.reader,
}
