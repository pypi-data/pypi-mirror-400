
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronsUpDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevrons-up-down'], 'items': [{'path': {'d': 'm7 15 5 5 5-5'}}, {'path': {'d': 'm7 9 5-5 5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
