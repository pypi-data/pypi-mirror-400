
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Tornado(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tornado'], 'items': [{'path': {'d': 'M21 4H3'}}, {'path': {'d': 'M18 8H6'}}, {'path': {'d': 'M19 12H9'}}, {'path': {'d': 'M16 16h-6'}}, {'path': {'d': 'M11 20H9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
