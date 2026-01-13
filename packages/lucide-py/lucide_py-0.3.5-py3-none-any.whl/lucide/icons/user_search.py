
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UserSearch(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-user-search'], 'items': [{'circle': {'cx': '10', 'cy': '7', 'r': '4'}}, {'path': {'d': 'M10.3 15H7a4 4 0 0 0-4 4v2'}}, {'circle': {'cx': '17', 'cy': '17', 'r': '3'}}, {'path': {'d': 'm21 21-1.9-1.9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
