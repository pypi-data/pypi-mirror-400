
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Minimize2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-minimize-2'], 'items': [{'path': {'d': 'm14 10 7-7'}}, {'path': {'d': 'M20 10h-6V4'}}, {'path': {'d': 'm3 21 7-7'}}, {'path': {'d': 'M4 14h6v6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
