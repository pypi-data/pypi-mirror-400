
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SearchCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-search-check'], 'items': [{'path': {'d': 'm8 11 2 2 4-4'}}, {'circle': {'cx': '11', 'cy': '11', 'r': '8'}}, {'path': {'d': 'm21 21-4.3-4.3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
