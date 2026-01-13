
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-x'], 'items': [{'path': {'d': 'M16 5H3'}}, {'path': {'d': 'M11 12H3'}}, {'path': {'d': 'M16 19H3'}}, {'path': {'d': 'm15.5 9.5 5 5'}}, {'path': {'d': 'm20.5 9.5-5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
