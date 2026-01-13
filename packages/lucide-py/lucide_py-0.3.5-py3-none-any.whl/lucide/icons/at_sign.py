
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AtSign(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-at-sign'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '4'}}, {'path': {'d': 'M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
