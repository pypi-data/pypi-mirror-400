
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveDiagonal2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-diagonal-2'], 'items': [{'path': {'d': 'M19 13v6h-6'}}, {'path': {'d': 'M5 11V5h6'}}, {'path': {'d': 'm5 5 14 14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
