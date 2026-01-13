
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Redo(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-redo'], 'items': [{'path': {'d': 'M21 7v6h-6'}}, {'path': {'d': 'M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
