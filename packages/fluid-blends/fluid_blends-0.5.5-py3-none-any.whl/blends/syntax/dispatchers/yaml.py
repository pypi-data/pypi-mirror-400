from blends.syntax.models import (
    Dispatcher,
)
from blends.syntax.readers.yaml import (
    block_mapping as yaml_block_mapping,
)
from blends.syntax.readers.yaml import (
    block_mapping_pair as yaml_block_mapping_pair,
)
from blends.syntax.readers.yaml import (
    block_sequence as yaml_block_sequence,
)
from blends.syntax.readers.yaml import (
    flow_node as yaml_flow_node,
)
from blends.syntax.readers.yaml import (
    stream as yaml_stream,
)

YAML_DISPATCHERS: Dispatcher = {
    "block_mapping": yaml_block_mapping.reader,
    "flow_mapping": yaml_block_mapping.reader,
    "block_mapping_pair": yaml_block_mapping_pair.reader,
    "flow_pair": yaml_block_mapping_pair.reader,
    "block_sequence": yaml_block_sequence.reader,
    "flow_node": yaml_flow_node.reader,
    "stream": yaml_stream.reader,
}
