
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevron-left'], 'items': [{'path': {'d': 'm15 18-6-6 6-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
