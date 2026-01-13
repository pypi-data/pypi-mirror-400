
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextSearch(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-search'], 'items': [{'path': {'d': 'M21 5H3'}}, {'path': {'d': 'M10 12H3'}}, {'path': {'d': 'M10 19H3'}}, {'circle': {'cx': '17', 'cy': '15', 'r': '3'}}, {'path': {'d': 'm21 19-1.9-1.9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
