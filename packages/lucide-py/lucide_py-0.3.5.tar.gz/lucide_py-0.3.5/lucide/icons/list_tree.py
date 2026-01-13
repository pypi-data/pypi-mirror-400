
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListTree(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-tree'], 'items': [{'path': {'d': 'M8 5h13'}}, {'path': {'d': 'M13 12h8'}}, {'path': {'d': 'M13 19h8'}}, {'path': {'d': 'M3 10a2 2 0 0 0 2 2h3'}}, {'path': {'d': 'M3 5v12a2 2 0 0 0 2 2h3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
