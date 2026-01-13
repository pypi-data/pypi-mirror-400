
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextCursor(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-cursor'], 'items': [{'path': {'d': 'M17 22h-1a4 4 0 0 1-4-4V6a4 4 0 0 1 4-4h1'}}, {'path': {'d': 'M7 22h1a4 4 0 0 0 4-4v-1'}}, {'path': {'d': 'M7 2h1a4 4 0 0 1 4 4v1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
