
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SearchCode(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-search-code'], 'items': [{'path': {'d': 'm13 13.5 2-2.5-2-2.5'}}, {'path': {'d': 'm21 21-4.3-4.3'}}, {'path': {'d': 'M9 8.5 7 11l2 2.5'}}, {'circle': {'cx': '11', 'cy': '11', 'r': '8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
