
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleDot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-dot'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
