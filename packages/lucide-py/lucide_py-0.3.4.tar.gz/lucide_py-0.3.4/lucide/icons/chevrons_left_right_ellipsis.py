
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronsLeftRightEllipsis(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevrons-left-right-ellipsis'], 'items': [{'path': {'d': 'M12 12h.01'}}, {'path': {'d': 'M16 12h.01'}}, {'path': {'d': 'm17 7 5 5-5 5'}}, {'path': {'d': 'm7 7-5 5 5 5'}}, {'path': {'d': 'M8 12h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
