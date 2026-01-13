
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Coffee(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-coffee'], 'items': [{'path': {'d': 'M10 2v2'}}, {'path': {'d': 'M14 2v2'}}, {'path': {'d': 'M16 8a1 1 0 0 1 1 1v8a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V9a1 1 0 0 1 1-1h14a4 4 0 1 1 0 8h-1'}}, {'path': {'d': 'M6 2v2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
