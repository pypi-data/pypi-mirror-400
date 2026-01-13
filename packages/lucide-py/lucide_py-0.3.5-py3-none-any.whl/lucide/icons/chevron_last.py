
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronLast(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevron-last'], 'items': [{'path': {'d': 'm7 18 6-6-6-6'}}, {'path': {'d': 'M17 6v12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
