
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-check'], 'items': [{'path': {'d': 'M16 5H3'}}, {'path': {'d': 'M16 12H3'}}, {'path': {'d': 'M11 19H3'}}, {'path': {'d': 'm15 18 2 2 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
