
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronsDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevrons-down'], 'items': [{'path': {'d': 'm7 6 5 5 5-5'}}, {'path': {'d': 'm7 13 5 5 5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
