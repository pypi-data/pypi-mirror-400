
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListCollapse(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-collapse'], 'items': [{'path': {'d': 'M10 5h11'}}, {'path': {'d': 'M10 12h11'}}, {'path': {'d': 'M10 19h11'}}, {'path': {'d': 'm3 10 3-3-3-3'}}, {'path': {'d': 'm3 20 3-3-3-3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
