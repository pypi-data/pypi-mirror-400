
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Undo(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-undo'], 'items': [{'path': {'d': 'M3 7v6h6'}}, {'path': {'d': 'M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
