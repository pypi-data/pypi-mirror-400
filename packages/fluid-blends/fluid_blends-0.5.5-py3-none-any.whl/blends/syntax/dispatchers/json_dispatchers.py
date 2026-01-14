from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.json import (
    array_node as json_array,
)
from blends.syntax.readers.json import (
    boolean as json_boolean,
)
from blends.syntax.readers.json import (
    comment as json_comment,
)
from blends.syntax.readers.json import (
    document as json_document,
)
from blends.syntax.readers.json import (
    number as json_number,
)
from blends.syntax.readers.json import (
    object as json_object,
)
from blends.syntax.readers.json import (
    pair as json_pair,
)
from blends.syntax.readers.json import (
    string_node as json_string,
)

JSON_DISPATCHERS: Dispatcher = {
    "array": json_array.reader,
    "false": json_boolean.reader,
    "true": json_boolean.reader,
    "comment": json_comment.reader,
    "document": json_document.reader,
    "number": json_number.reader,
    "object": json_object.reader,
    "pair": json_pair.reader,
    "string": json_string.reader,
}
