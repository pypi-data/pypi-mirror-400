
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextInitial(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-initial'], 'items': [{'path': {'d': 'M15 5h6'}}, {'path': {'d': 'M15 12h6'}}, {'path': {'d': 'M3 19h18'}}, {'path': {'d': 'm3 12 3.553-7.724a.5.5 0 0 1 .894 0L11 12'}}, {'path': {'d': 'M3.92 10h6.16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
