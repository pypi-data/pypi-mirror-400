
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Vegan(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-vegan'], 'items': [{'path': {'d': 'M16 8q6 0 6-6-6 0-6 6'}}, {'path': {'d': 'M17.41 3.59a10 10 0 1 0 3 3'}}, {'path': {'d': 'M2 2a26.6 26.6 0 0 1 10 20c.9-6.82 1.5-9.5 4-14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
