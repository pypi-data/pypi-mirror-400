
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListChevronsDownUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-chevrons-down-up'], 'items': [{'path': {'d': 'M3 5h8'}}, {'path': {'d': 'M3 12h8'}}, {'path': {'d': 'M3 19h8'}}, {'path': {'d': 'm15 5 3 3 3-3'}}, {'path': {'d': 'm15 19 3-3 3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
