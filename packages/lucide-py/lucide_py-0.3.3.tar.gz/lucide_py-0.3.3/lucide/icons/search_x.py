
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SearchX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-search-x'], 'items': [{'path': {'d': 'm13.5 8.5-5 5'}}, {'path': {'d': 'm8.5 8.5 5 5'}}, {'circle': {'cx': '11', 'cy': '11', 'r': '8'}}, {'path': {'d': 'm21 21-4.3-4.3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
