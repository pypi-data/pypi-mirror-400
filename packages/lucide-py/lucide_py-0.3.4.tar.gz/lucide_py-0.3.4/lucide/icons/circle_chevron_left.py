
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleChevronLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-chevron-left'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm14 16-4-4 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
