
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Eye(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-eye'], 'items': [{'path': {'d': 'M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
