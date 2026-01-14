from enum import Enum


class StackGraphNodeKind(str, Enum):
    DROP_SCOPES = "DropScopesNode"
    JUMP_TO = "JumpToNode"
    POP_SCOPED_SYMBOL = "PopScopedSymbolNode"
    POP_SYMBOL = "PopSymbolNode"
    PUSH_SCOPED_SYMBOL = "PushScopedSymbolNode"
    PUSH_SYMBOL = "PushSymbolNode"
    ROOT = "RootNode"
    SCOPE = "ScopeNode"


_VALID_STACK_GRAPH_KINDS = {kind.value for kind in StackGraphNodeKind}


def is_stack_graph_kind(value: object) -> bool:
    if not isinstance(value, str):
        return False
    return value in _VALID_STACK_GRAPH_KINDS
