
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Unlink2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-unlink-2'], 'items': [{'path': {'d': 'M15 7h2a5 5 0 0 1 0 10h-2m-6 0H7A5 5 0 0 1 7 7h2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
