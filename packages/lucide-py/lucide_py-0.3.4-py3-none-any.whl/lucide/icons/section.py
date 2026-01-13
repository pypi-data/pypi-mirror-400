
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Section(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-section'], 'items': [{'path': {'d': 'M16 5a4 3 0 0 0-8 0c0 4 8 3 8 7a4 3 0 0 1-8 0'}}, {'path': {'d': 'M8 19a4 3 0 0 0 8 0c0-4-8-3-8-7a4 3 0 0 1 8 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
