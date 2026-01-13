
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Headphones(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-headphones'], 'items': [{'path': {'d': 'M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
