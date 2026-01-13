
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Infinity(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-infinity'], 'items': [{'path': {'d': 'M6 16c5 0 7-8 12-8a4 4 0 0 1 0 8c-5 0-7-8-12-8a4 4 0 1 0 0 8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
