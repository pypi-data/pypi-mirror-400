
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevron-up'], 'items': [{'path': {'d': 'm18 15-6-6-6 6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
