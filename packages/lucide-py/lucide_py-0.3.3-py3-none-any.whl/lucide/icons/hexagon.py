
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Hexagon(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-hexagon'], 'items': [{'path': {'d': 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
