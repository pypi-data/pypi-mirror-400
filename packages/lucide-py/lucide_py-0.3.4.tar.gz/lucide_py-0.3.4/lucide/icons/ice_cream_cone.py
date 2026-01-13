
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def IceCreamCone(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-ice-cream-cone'], 'items': [{'path': {'d': 'm7 11 4.08 10.35a1 1 0 0 0 1.84 0L17 11'}}, {'path': {'d': 'M17 7A5 5 0 0 0 7 7'}}, {'path': {'d': 'M17 7a2 2 0 0 1 0 4H7a2 2 0 0 1 0-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
