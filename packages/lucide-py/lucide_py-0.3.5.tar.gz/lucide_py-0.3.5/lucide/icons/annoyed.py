
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Annoyed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-annoyed'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M8 15h8'}}, {'path': {'d': 'M8 9h2'}}, {'path': {'d': 'M14 9h2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
