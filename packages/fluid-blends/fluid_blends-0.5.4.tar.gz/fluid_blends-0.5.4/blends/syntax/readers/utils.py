from blends.models import NId
from blends.syntax.models import ReaderLogicError


def check_reader_element_consistency(*args: NId) -> None:
    if any(arg is None for arg in args):
        msg = "Inconsistent reader element"
        raise ReaderLogicError(msg)
