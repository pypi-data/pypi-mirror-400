
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BottleWine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bottle-wine'], 'items': [{'path': {'d': 'M10 3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2a6 6 0 0 0 1.2 3.6l.6.8A6 6 0 0 1 17 13v8a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1v-8a6 6 0 0 1 1.2-3.6l.6-.8A6 6 0 0 0 10 5z'}}, {'path': {'d': 'M17 13h-4a1 1 0 0 0-1 1v3a1 1 0 0 0 1 1h4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
