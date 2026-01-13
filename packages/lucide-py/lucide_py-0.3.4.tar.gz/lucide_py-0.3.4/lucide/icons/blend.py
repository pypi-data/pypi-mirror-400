
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Blend(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-blend'], 'items': [{'circle': {'cx': '9', 'cy': '9', 'r': '7'}}, {'circle': {'cx': '15', 'cy': '15', 'r': '7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
