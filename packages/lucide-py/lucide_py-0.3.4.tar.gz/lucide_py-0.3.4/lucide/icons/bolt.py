
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Bolt(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bolt'], 'items': [{'path': {'d': 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
