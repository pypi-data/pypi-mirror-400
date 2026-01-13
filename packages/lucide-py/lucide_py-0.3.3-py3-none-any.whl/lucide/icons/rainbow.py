
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Rainbow(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rainbow'], 'items': [{'path': {'d': 'M22 17a10 10 0 0 0-20 0'}}, {'path': {'d': 'M6 17a6 6 0 0 1 12 0'}}, {'path': {'d': 'M10 17a2 2 0 0 1 4 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
