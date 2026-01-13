
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Music(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-music'], 'items': [{'path': {'d': 'M9 18V5l12-2v13'}}, {'circle': {'cx': '6', 'cy': '18', 'r': '3'}}, {'circle': {'cx': '18', 'cy': '16', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
