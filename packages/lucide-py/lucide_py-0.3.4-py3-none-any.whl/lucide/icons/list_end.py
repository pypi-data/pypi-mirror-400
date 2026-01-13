
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListEnd(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-end'], 'items': [{'path': {'d': 'M16 5H3'}}, {'path': {'d': 'M16 12H3'}}, {'path': {'d': 'M9 19H3'}}, {'path': {'d': 'm16 16-3 3 3 3'}}, {'path': {'d': 'M21 5v12a2 2 0 0 1-2 2h-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
