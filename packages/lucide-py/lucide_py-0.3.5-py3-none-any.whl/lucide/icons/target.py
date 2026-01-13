
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Target(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-target'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '6'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
