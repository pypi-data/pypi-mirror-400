
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleMinus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-minus'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M8 12h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
