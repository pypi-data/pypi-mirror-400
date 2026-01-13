
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Navigation(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-navigation'], 'items': [{'polygon': {'points': '3 11 22 2 13 21 11 13 3 11'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
