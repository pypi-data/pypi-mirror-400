
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListPlus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-plus'], 'items': [{'path': {'d': 'M16 5H3'}}, {'path': {'d': 'M11 12H3'}}, {'path': {'d': 'M16 19H3'}}, {'path': {'d': 'M18 9v6'}}, {'path': {'d': 'M21 12h-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
