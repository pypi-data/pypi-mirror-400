
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Minus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-minus'], 'items': [{'path': {'d': 'M5 12h14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
