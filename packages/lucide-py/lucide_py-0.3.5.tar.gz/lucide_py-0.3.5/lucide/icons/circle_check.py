
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-check'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm9 12 2 2 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
