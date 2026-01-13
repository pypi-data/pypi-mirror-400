
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevron-down'], 'items': [{'path': {'d': 'm6 9 6 6 6-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
