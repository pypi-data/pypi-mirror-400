
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Navigation2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-navigation-2'], 'items': [{'polygon': {'points': '12 2 19 21 12 17 5 21 12 2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
