
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RectangleCircle(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rectangle-circle'], 'items': [{'path': {'d': 'M14 4v16H3a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z'}}, {'circle': {'cx': '14', 'cy': '12', 'r': '8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
