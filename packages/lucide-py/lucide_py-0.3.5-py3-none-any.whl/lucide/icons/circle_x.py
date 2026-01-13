
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-x'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm15 9-6 6'}}, {'path': {'d': 'm9 9 6 6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
