
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Rss(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rss'], 'items': [{'path': {'d': 'M4 11a9 9 0 0 1 9 9'}}, {'path': {'d': 'M4 4a16 16 0 0 1 16 16'}}, {'circle': {'cx': '5', 'cy': '19', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
