
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Copyleft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-copyleft'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M9.17 14.83a4 4 0 1 0 0-5.66'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
