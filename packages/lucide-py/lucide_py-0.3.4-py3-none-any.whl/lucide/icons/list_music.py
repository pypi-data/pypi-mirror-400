
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListMusic(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-music'], 'items': [{'path': {'d': 'M16 5H3'}}, {'path': {'d': 'M11 12H3'}}, {'path': {'d': 'M11 19H3'}}, {'path': {'d': 'M21 16V5'}}, {'circle': {'cx': '18', 'cy': '16', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
