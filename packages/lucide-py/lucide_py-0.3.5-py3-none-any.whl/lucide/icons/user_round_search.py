
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UserRoundSearch(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-user-round-search'], 'items': [{'circle': {'cx': '10', 'cy': '8', 'r': '5'}}, {'path': {'d': 'M2 21a8 8 0 0 1 10.434-7.62'}}, {'circle': {'cx': '18', 'cy': '18', 'r': '3'}}, {'path': {'d': 'm22 22-1.9-1.9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
