
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Dot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-dot'], 'items': [{'circle': {'cx': '12.1', 'cy': '12.1', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
