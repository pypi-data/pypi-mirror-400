
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Circle(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
