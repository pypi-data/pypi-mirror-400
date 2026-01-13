
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Gavel(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-gavel'], 'items': [{'path': {'d': 'm14 13-8.381 8.38a1 1 0 0 1-3.001-3l8.384-8.381'}}, {'path': {'d': 'm16 16 6-6'}}, {'path': {'d': 'm21.5 10.5-8-8'}}, {'path': {'d': 'm8 8 6-6'}}, {'path': {'d': 'm8.5 7.5 8 8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
