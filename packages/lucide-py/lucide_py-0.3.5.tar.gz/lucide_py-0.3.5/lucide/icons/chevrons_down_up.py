
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronsDownUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevrons-down-up'], 'items': [{'path': {'d': 'm7 20 5-5 5 5'}}, {'path': {'d': 'm7 4 5 5 5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
