
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListMinus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-minus'], 'items': [{'path': {'d': 'M16 5H3'}}, {'path': {'d': 'M11 12H3'}}, {'path': {'d': 'M16 19H3'}}, {'path': {'d': 'M21 12h-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
